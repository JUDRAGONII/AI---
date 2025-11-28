"""直接使用yfinance寫入台積電價格"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime, timedelta
from data_loader import DatabaseConnector
from loguru import logger

db = DatabaseConnector()

# 獲取台積電近30天數據
stock = yf.Ticker('2330.TW')
df = stock.history(period='1mo')

logger.info(f"獲取{len(df)}筆數據")

# 轉換並寫入
price_records = []
for date, row in df.iterrows():
    price_records.append({
        'stock_code': '2330',
        'trade_date': date.date(),
        'open_price': float(row['Open']),
        'high_price': float(row['High']),
        'low_price': float(row['Low']),
        'close_price': float(row['Close']),
        'volume': int(row['Volume'])
    })

count = db.bulk_insert('tw_stock_prices', price_records)
logger.info(f"✅ 寫入{count}筆")

# 驗證
result = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")
logger.info(f"資料庫總計: {result[0]['c']}筆")

db.close()
