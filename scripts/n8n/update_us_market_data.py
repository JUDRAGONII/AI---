"""
N8N 自動化腳本 - 美股收盤數據更新
用於每日清晨 5:30 (05:30) 執行，更新前一日收盤數據
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

from api_clients.us_stock_client import USStockClient
from data_loader import DatabaseConnector

def update_us_market_data():
    """更新美股市場數據（針對關注列表和持倉）"""
    
    logger.info("=" * 60)
    logger.info("🚀 [N8N] 開始執行美股收盤數據更新")
    logger.info("=" * 60)
    
    db = DatabaseConnector()
    client = USStockClient()
    
    try:
        # 1. 獲取需要更新的股票清單
        logger.info("🔍 獲取目標股票清單...")
        
        # 查詢用戶持倉
        holdings = db.execute_query("""
            SELECT DISTINCT stock_code 
            FROM portfolio_holdings 
            WHERE market = 'US'
        """)
        
        # 查詢系統預設 (S&P 500 Top & ETFs)
        default_stocks = [
            'SPY', 'QQQ', 'DIA', 'IWM', 'VXX',      # 大盤 ETF
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', # 科技巨頭
            'TSLA', 'META', 'BRK.B', 'TSM', 'AMD',   # 熱門股
            'TLT', 'IEF', 'GLD', 'SLV', 'USO'       # 資產類 ETF
        ]
        
        target_codes = set(default_stocks)
        if holdings:
            for h in holdings:
                target_codes.add(h['stock_code'])
        
        logger.info(f"📋 目標股票共 {len(target_codes)} 支")
        
        # 2. 定義更新範圍
        # 美股收盤時間是清晨，其實是抓「昨天」的 K 線
        # yfinance 的 end date 是 exclusive
        today = datetime.now().date()
        date_str = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=5)).strftime('%Y-%m-%d')
        
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
                        'market': 'US'
                    })
                
                # 寫入 us_stock_prices 表
                query = """
                    INSERT INTO us_stock_prices 
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
                
                time.sleep(1.0) # 美股 API 限制可能較嚴格 (Tiingo)
                
            except Exception as e:
                logger.error(f"❌ 更新 {code} 失敗: {e}")
                error_count += 1
        
        logger.info("=" * 60)
        logger.info("📊 更新統計")
        logger.info(f"   目標股票: {len(target_codes)}")
        logger.info(f"   成功更新: {updated_count}")
        logger.info(f"   跳過/無資料: {skipped_count}")
        logger.info(f"   錯誤: {error_count}")
        logger.info("=" * 60)
        logger.info("✅ 美股收盤數據更新完成")
        
    except Exception as e:
        logger.error(f"❌ 腳本執行失敗: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    update_us_market_data()
