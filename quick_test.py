"""
快速測試資料回溯
直接使用硬編碼配置
"""
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_clients.tw_stock_client import TWStockClient
from api_clients.us_stock_client import USStockClient
from loguru import logger

# 硬編碼資料庫配置（使用正確端口）
DB_CONFIG = {
    'host': 'localhost',
    'port': 15432,  # 使用新端口
    'database': 'financial_data',
    'user': 'postgres',
    'password': '0824-003-a-8-Po'
}

logger.info("=" * 70)
logger.info("🚀 開始測試資料回溯（台積電 + Apple）")
logger.info("=" * 70)

# 測試台股
logger.info("\n[1/2] 回溯台積電資料...")
try:
    tw_client = TWStockClient()
    df = tw_client.get_daily_price('2330', '2024-11-01', '2024-11-22')
    
    if not df.empty:
        logger.success(f"✅ 成功取得 {len(df)} 筆台積電資料")
        
        # 寫入資料庫
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO tw_stock_prices 
                (stock_code, trade_date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code, trade_date) DO UPDATE SET
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume
            """, ('2330', row['trade_date'], row['open'], row['high'], row['low'], 
                  row['close'], row['volume'], row.get('adjusted_close', row['close'])))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.success(f"✅ 成功寫入 {len(df)} 筆台積電資料至資料庫")
    else:
        logger.warning("⚠️  未取得台積電資料")
        
except Exception as e:
    logger.error(f"❌ 台積電回溯失敗: {e}")

# 測試美股
logger.info("\n[2/2] 回溯 Apple 資料...")
try:
    us_client = USStockClient()
    df = us_client.get_daily_price('AAPL', '2024-11-01', '2024-11-22')
    
    if not df.empty:
        logger.success(f"✅ 成功取得 {len(df)} 筆 Apple 資料")
        
        # 寫入資料庫
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO us_stock_prices 
                (symbol, trade_date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, trade_date) DO UPDATE SET
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume
            """, ('AAPL', row['trade_date'], row['open'], row['high'], row['low'], 
                  row['close'], row['volume'], row.get('adjusted_close', row['close'])))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.success(f"✅ 成功寫入 {len(df)} 筆 Apple 資料至資料庫")
    else:
        logger.warning("⚠️  未取得 Apple 資料")
        
except Exception as e:
    logger.error(f"❌ Apple 回溯失敗: {e}")

logger.info("\n" + "=" * 70)
logger.success("🎉 測試資料回溯完成！")
logger.info("=" * 70)
logger.info("\n💡 現在可以在 pgAdmin 查看資料：")
logger.info("   1. 開啟 http://localhost:8080")
logger.info("   2. 執行查詢：SELECT COUNT(*) FROM tw_stock_prices;")
logger.info("   3. 執行查詢：SELECT COUNT(*) FROM us_stock_prices;")
logger.info("")
