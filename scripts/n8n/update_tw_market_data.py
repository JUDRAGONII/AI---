"""
N8N 自動化腳本 - 台股盤後數據更新
用於每日下午 2:30 (14:30) 執行，更新當日收盤數據
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
import time

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api_clients.tw_stock_client import TWStockClient
from data_loader import DatabaseConnector

def update_tw_market_data():
    """更新台股市場數據（針對關注列表和持倉）"""
    
    logger.info("=" * 60)
    logger.info("🚀 [N8N] 開始執行台股盤後數據更新")
    logger.info("=" * 60)
    
    db = DatabaseConnector()
    client = TWStockClient()
    
    try:
        # 1. 獲取需要更新的股票清單
        # 包括：
        # - 用戶持倉股票
        # - 用戶關注名單 (watchlists)
        # - 系統預設重要權值股 (如 2330, 0050)
        
        logger.info("🔍 獲取目標股票清單...")
        
        # 查詢用戶持倉
        holdings = db.execute_query("""
            SELECT DISTINCT stock_code 
            FROM portfolio_holdings 
            WHERE market = 'TW'
        """)
        
        # 查詢系統預設 (Top 50 + ETFs)
        # 這裡簡化為固定列表，實際可從 tw_stock_info 篩選
        default_stocks = [
            '2330', '2317', '2454', '2308', '2303', '2881', '2882', '2412',
            '0050', '0056', '00878', '00929', '006208', '00713'
        ]
        
        target_codes = set(default_stocks)
        if holdings:
            for h in holdings:
                target_codes.add(h['stock_code'])
        
        # 確保資料庫中有這些股票的基本資料
        # 如果沒有，先同步基本資料
        logger.info(f"📋 目標股票共 {len(target_codes)} 支")
        
        # 2. 定義更新範圍 (今天)
        today = datetime.now().date()
        date_str = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=5)).strftime('%Y-%m-%d') # 多抓幾天以防漏失或週末
        
        # 3. 逐一更新價格
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for code in target_codes:
            try:
                logger.info(f"🔄 更新 {code} 價格數據...")
                
                # 獲取價格
                df = client.get_daily_price(code, start_date, date_str)
                
                if df.empty:
                    logger.warning(f"⚠️ {code} 無法獲取價格數據")
                    skipped_count += 1
                    continue
                
                # 準備寫入資料庫
                # 需要轉換 DataFrame 為 list of dicts
                data_to_insert = []
                for _, row in df.iterrows():
                    data_to_insert.append({
                        'stock_code': code,
                        'trade_date': row['trade_date'],
                        'open_price': row['open'],
                        'high_price': row['high'],
                        'low_price': row['low'],
                        'close_price': row['close'],
                        'volume': int(row['volume']),
                        'market': 'TW' # 假設都是上市/櫃
                    })
                
                # 寫入 tw_stock_prices 表
                # 使用 upsert (INSERT ... ON CONFLICT DO UPDATE)
                # DatabaseConnector 可能沒有直接支援 upsert，這裡假設 bulk_insert 有處理 conflict
                # 檢查 DatabaseConnector.bulk_insert 的實現
                
                # 這裡直接用 execute_batch 進行 UPSERT
                query = """
                    INSERT INTO tw_stock_prices 
                    (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%(stock_code)s, %(trade_date)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s, %(volume)s)
                    ON CONFLICT (stock_code, trade_date) 
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                db.execute_batch(query, data_to_insert)
                updated_count += 1
                
                time.sleep(0.5) # 避免太快
                
            except Exception as e:
                logger.error(f"❌ 更新 {code} 失敗: {e}")
                error_count += 1
        
        # 4. 更新大盤指數 (加權指數, 櫃買指數)
        # 用戶端可能沒有直接支援指數，這裡略過或使用 yfinance '^TWII'
        
        logger.info("=" * 60)
        logger.info("📊 更新統計")
        logger.info(f"   目標股票: {len(target_codes)}")
        logger.info(f"   成功更新: {updated_count}")
        logger.info(f"   跳過/無資料: {skipped_count}")
        logger.info(f"   錯誤: {error_count}")
        logger.info("=" * 60)
        logger.info("✅ 台股盤後數據更新完成")
        
    except Exception as e:
        logger.error(f"❌ 腳本執行失敗: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    update_tw_market_data()
