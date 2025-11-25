"""
完整資料回溯執行腳本 - 支援 Phase 1-5
包含詳細進度追蹤、錯誤處理、斷點續傳
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import BACKFILL_PHASES
from api_clients.tw_stock_client import TWStockClient
from api_clients.us_stock_client import USStockClient
from api_clients.gold_client import GoldClient
from api_clients.exchange_rate_client import ExchangeRateClient
from api_clients.macro_client import MacroClient
from api_clients.news_client import NewsClient
from data_loader.database_writer import DatabaseWriter
from loguru import logger


def backfill_phase_1(writer: DatabaseWriter):
    """Phase 1: 基礎參考資料（黃金、匯率）"""
    logger.info("=" * 70)
    logger.info("🔹 Phase 1: 基礎參考資料（黃金、匯率）")
    logger.info("   預估時間：2-3 天")
    logger.info("=" * 70)
    
    # 1. 黃金價格（自 1968年）
    logger.info("\n[1/2] 📊 回溯黃金價格（1968-至今）...")
    gold_client = GoldClient()
    
    try:
        df = gold_client.get_daily_price('1968-01-01')
        if not df.empty:
            logger.success(f"✅ 黃金價格：取得 {len(df)} 筆資料")
            writer.insert_gold_prices(df)
            
            writer.update_sync_status(
                data_source='gold',
                source_identifier='XAU/USD',
                status='success',
                earliest_date=df['trade_date'].min(),
                latest_date=df['trade_date'].max(),
                total_records=len(df)
            )
        else:
            logger.warning("⚠️  黃金價格：無資料")
    except Exception as e:
        logger.error(f"❌ 黃金價格回溯失敗: {e}")
    
    # 2. TWD/USD 匯率（自 1990年）
    logger.info("\n[2/2] 💱 回溯 TWD/USD 匯率（1990-至今）...")
    fx_client = ExchangeRateClient()
    
    try:
        df = fx_client.get_rate_series('USD', 'TWD', '1990-01-01')
        if not df.empty:
            logger.success(f"✅ TWD/USD 匯率：取得 {len(df)} 筆資料")
            writer.insert_exchange_rates(df)
            
            writer.update_sync_status(
                data_source='exchange_rate',
                source_identifier='TWD/USD',
                status='success',
                earliest_date=df['trade_date'].min(),
                latest_date=df['trade_date'].max(),
                total_records=len(df)
            )
        else:
            logger.warning("⚠️  TWD/USD 匯率：無資料")
    except Exception as e:
        logger.error(f"❌ 匯率回溯失敗: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.success("✅ Phase 1 完成！")
    logger.info("=" * 70)


def backfill_phase_2(writer: DatabaseWriter):
    """Phase 2: 宏觀經濟指標"""
    logger.info("=" * 70)
    logger.info("🔹 Phase 2: 宏觀經濟指標")
    logger.info("   預估時間：3-5 天")
    logger.info("=" * 70)
    
    macro_client = MacroClient()
    
    # 美國核心經濟指標
    logger.info("\n📈 回溯美國核心經濟指標（1960-至今）...")
    
    try:
        data = macro_client.get_us_core_indicators('1960-01-01')
        
        for indicator, df in data.items():
            if not df.empty:
                # 確保有 indicator_type 欄位
                df['indicator_type'] = indicator
                logger.success(f"✅ {indicator}: {len(df)} 筆")
                writer.insert_macro_data(df)
                
                writer.update_sync_status(
                    data_source='macro',
                    source_identifier=indicator,
                    status='success',
                    earliest_date=df['release_date'].min(),
                    latest_date=df['release_date'].max(),
                    total_records=len(df)
                )
            else:
                logger.warning(f"⚠️  {indicator}: 無資料")
                
    except Exception as e:
        logger.error(f"❌ 宏觀經濟指標回溯失敗: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.success("✅ Phase 2 完成！")
    logger.info("=" * 70)


def backfill_phase_3(writer: DatabaseWriter, mode='full'):
    """Phase 3: 台股資料"""
    logger.info("=" * 70)
    logger.info("🔹 Phase 3: 台股資料")
    logger.info("   預估時間：10-14 天")
    logger.info("=" * 70)
    
    client = TWStockClient()
    
    # 取得股票清單
    if mode == 'full':
        # 先回溯 Top 100
        logger.info("\n[1/2] 📊 回溯台股 Top 100（市值前100大）...")
        stock_codes = client.get_top_stocks(100)
    else:
        # 測試模式：只回溯台積電
        logger.info("\n🧪 測試模式：只回溯台積電...")
        stock_codes = ['2330']
    
    start_date = '2000-01-01'
    success_count = 0
    fail_count = 0
    total_records = 0
    
    with tqdm(total=len(stock_codes), desc="台股回溯進度") as pbar:
        for stock_code in stock_codes:
            try:
                df = client.get_daily_price(stock_code, start_date)
                
                if not df.empty:
                    df['stock_code'] = stock_code
                    
                    # 確保基本資料存在
                    writer.ensure_tw_stock_exists(stock_code)
                    
                    # 寫入資料庫
                    count = writer.insert_tw_stock_prices(df)
                    total_records += count
                    
                    # 更新同步狀態
                    writer.update_sync_status(
                        data_source='taiwan_stock',
                        source_identifier=stock_code,
                        status='success',
                        earliest_date=df['trade_date'].min(),
                        latest_date=df['trade_date'].max(),
                        total_records=count
                    )
                    
                    success_count += 1
                    pbar.set_postfix({'成功': success_count, '失敗': fail_count, '總筆數': total_records})
                else:
                    fail_count += 1
                    logger.warning(f"{stock_code}: 無資料")
                    
            except Exception as e:
                fail_count += 1
                logger.error(f"{stock_code} 失敗: {e}")
                
                writer.update_sync_status(
                    data_source='taiwan_stock',
                    source_identifier=stock_code,
                    status='failed',
                    error_message=str(e)
                )
            
            pbar.update(1)
            time.sleep(0.5)  # 避免請求過快
    
    logger.info("\n" + "=" * 70)
    logger.success(f"✅ Phase 3 完成！成功：{success_count}，失敗：{fail_count}，總計：{total_records} 筆")
    logger.info("=" * 70)


def backfill_phase_4(writer: DatabaseWriter, mode='full'):
    """Phase 4: 美股資料"""
    logger.info("=" * 70)
    logger.info("🔹 Phase 4: 美股資料")
    logger.info("   預估時間：30-45 天")
    logger.info("=" * 70)
    
    client = USStockClient()
    
    # 取得股票清單
    if mode == 'full':
        logger.info("\n[1/2] 📊 回溯 S&P 500 成分股...")
        stock_symbols = client.get_sp500_list()[:50]  # 先回溯前 50 支
    else:
        # 測試模式：只回溯 AAPL
        logger.info("\n🧪 測試模式：只回溯 Apple...")
        stock_symbols = ['AAPL']
    
    start_date = '1970-01-01'
    success_count = 0
    fail_count = 0
    total_records = 0
    
    with tqdm(total=len(stock_symbols), desc="美股回溯進度") as pbar:
        for symbol in stock_symbols:
            try:
                df = client.get_daily_price(symbol, start_date)
                
                if not df.empty:
                    df['symbol'] = symbol
                    
                    # 確保基本資料存在
                    writer.ensure_us_stock_exists(symbol)
                    
                    # 寫入資料庫
                    count = writer.insert_us_stock_prices(df)
                    total_records += count
                    
                    # 更新同步狀態
                    writer.update_sync_status(
                        data_source='us_stock',
                        source_identifier=symbol,
                        status='success',
                        earliest_date=df['trade_date'].min(),
                        latest_date=df['trade_date'].max(),
                        total_records=count
                    )
                    
                    success_count += 1
                    pbar.set_postfix({'成功': success_count, '失敗': fail_count, '總筆數': total_records})
                else:
                    fail_count += 1
                    logger.warning(f"{symbol}: 無資料")
                    
            except Exception as e:
                fail_count += 1
                logger.error(f"{symbol} 失敗: {e}")
                
                writer.update_sync_status(
                    data_source='us_stock',
                    source_identifier=symbol,
                    status='failed',
                    error_message=str(e)
                )
            
            pbar.update(1)
            time.sleep(1.0)  # 避免請求過快
    
    logger.info("\n" + "=" * 70)
    logger.success(f"✅ Phase 4 完成！成功：{success_count}，失敗：{fail_count}，總計：{total_records} 筆")
    logger.info("=" * 70)


def backfill_phase_5(writer: DatabaseWriter):
    """Phase 5: 金融新聞"""
    logger.info("=" * 70)
    logger.info("🔹 Phase 5: 金融新聞")
    logger.info("   預估時間：1-2 天")
    logger.info("=" * 70)
    
    news_client = NewsClient()
    
    logger.info("\n📰 回溯最近市場新聞...")
    
    try:
        news_list = news_client.get_market_news(limit=100)
        
        if news_list:
            logger.success(f"✅ 成功取得 {len(news_list)} 則新聞")
            writer.insert_financial_news(news_list)
            
            writer.update_sync_status(
                data_source='news',
                source_identifier='market_news',
                status='success',
                total_records=len(news_list)
            )
            
            # 顯示前 5 則標題
            logger.info("\n最新新聞預覽：")
            for i, news in enumerate(news_list[:5], 1):
                logger.info(f"  {i}. {news['title'][:60]}...")
        else:
            logger.warning("⚠️  無新聞資料")
            
    except Exception as e:
        logger.error(f"❌ 新聞回溯失敗: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.success("✅ Phase 5 完成！")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='📊 金融資料庫歷史資料回溯系統')
    parser.add_argument('--phase', type=int, choices=[1,2,3,4,5], help='執行特定階段 (1-5)')
    parser.add_argument('--mode', choices=['full', 'test'], default='test', help='執行模式：full(完整) 或 test(測試)')
    
    args = parser.parse_args()
    
    # 顯示啟動訊息
    logger.info("\n" + "=" * 70)
    logger.info("🚀 金融資料庫歷史資料回溯系統")
    logger.info("=" * 70)
    logger.info(f"⚙️  執行模式: {args.mode.upper()}")
    logger.info(f"📋 執行階段: Phase {args.phase if args.phase else 'ALL (1-5)'}")
    logger.info(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 連接資料庫
    try:
        with DatabaseWriter() as writer:
            start_time = time.time()
            
            # 執行指定階段
            if args.phase:
                # 單一階段
                phase_functions = {
                    1: backfill_phase_1,
                    2: backfill_phase_2,
                    3: lambda w: backfill_phase_3(w, args.mode),
                    4: lambda w: backfill_phase_4(w, args.mode),
                    5: backfill_phase_5
                }
                
                phase_functions[args.phase](writer)
                
            elif args.mode == 'test':
                # 測試模式：快速測試各階段
                logger.info("\n🧪 測試模式：執行快速驗證...")
                logger.info("   Phase 3: 台積電 (2330)")
                logger.info("   Phase 4: Apple (AAPL)")
                logger.info("")
                
                backfill_phase_3(writer, mode='test')
                time.sleep(2)
                backfill_phase_4(writer, mode='test')
                
            else:
                # 完整模式：執行所有階段
                logger.info("\n📋 完整模式：將依序執行 Phase 1-5")
                logger.warning("   ⚠️  預計總時間：60-90 天（建議背景執行）")
                logger.info("")
                
                for phase_num in range(1, 6):
                    logger.info(f"\n▶️  準備執行 Phase {phase_num}...")
                    time.sleep(2)
                    
                    if phase_num <= 2 or phase_num == 5:
                        phase_functions = {
                            1: backfill_phase_1,
                            2: backfill_phase_2,
                            5: backfill_phase_5
                        }
                        phase_functions[phase_num](writer)
                    else:
                        if phase_num == 3:
                            backfill_phase_3(writer, mode='full')
                        elif phase_num == 4:
                            backfill_phase_4(writer, mode='full')
            
            # 計算執行時間
            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            
            # 最終總結
            logger.info("\n" + "=" * 70)
            logger.success("🎉 資料回溯完成！")
            logger.info("=" * 70)
            logger.info(f"⏱️  執行時間: {minutes} 分 {seconds} 秒")
            logger.info(f"🕐 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 70)
            logger.info("\n💡 下一步：")
            logger.info("   1. 查看資料：使用 pgAdmin (http://localhost:8080)")
            logger.info("   2. 驗證資料：python scripts/verify_data.py")
            logger.info("   3. 開始分析：整合至 AI 投資分析儀")
            logger.info("")
            
    except Exception as e:
        logger.error(f"\n❌ 執行失敗: {e}")
        logger.exception("詳細錯誤訊息：")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
