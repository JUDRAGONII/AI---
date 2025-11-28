"""
美股數據同步：S&P 500前100支
自動執行
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from data_loader import DatabaseConnector
from loguru import logger
import time

# S&P 500 代表性股票（科技、金融、消費等）
SP500_TOP = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
    'XOM', 'V', 'PG', 'JPM', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
    'KO', 'AVGO', 'COST', 'LLY', 'WMT', 'MCD', 'CSCO', 'ACN', 'TMO', 'ABT',
    'DIS', 'VZ', 'ADBE', 'NFLX', 'NKE', 'CMCSA', 'CRM', 'DHR', 'TXN', 'INTC',
    'NEE', 'PM', 'UPS', 'RTX', 'ORCL', 'QCOM', 'HON', 'INTU', 'LOW', 'AMD'
]

db = DatabaseConnector()
success = 0
prices = 0

logger.info(f"開始同步美股前50支")

try:
    for i, symbol in enumerate(SP500_TOP, 1):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            
            # 寫入us_stock_info
            db.execute_query("""
                INSERT INTO us_stock_info (stock_code, stock_name, exchange, sector)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = EXCLUDED.stock_name,
                    sector = EXCLUDED.sector
            """, (symbol, name[:100], 'US', sector[:50]))
            
            # 獲取3個月價格
            df = ticker.history(period='3mo')
            
            if not df.empty:
                for date, row in df.iterrows():
                    db.execute_query("""
                        INSERT INTO us_stock_prices 
                        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price
                    """, (symbol, date.date(), float(row['Open']), float(row['High']),
                          float(row['Low']), float(row['Close']), int(row['Volume'])))
                
                success += 1
                prices += len(df)
            
            if i % 10 == 0:
                logger.info(f"進度: {i}/50 - 成功{success}支")
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"{symbol}: {str(e)[:40]}")
    
    r1 = db.execute_query("SELECT COUNT(*) as c FROM us_stock_info")[0]
    r2 = db.execute_query("SELECT COUNT(*) as c FROM us_stock_prices")[0]
    
    logger.info(f"✅ 美股同步完成 - {r1['c']}支, {r2['c']}筆")
    
finally:
    db.close()
