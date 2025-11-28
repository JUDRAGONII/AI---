"""
簡化版技術指標計算 - 適配實際表結構
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from data_loader import DatabaseConnector
from loguru import logger

db = DatabaseConnector()

logger.info("📊 計算技術指標（簡化版）")

try:
    # 只處理有足夠數據的股票
    stocks = db.execute_query("""
        SELECT stock_code, COUNT(*) as cnt 
        FROM tw_stock_prices 
        GROUP BY stock_code 
        HAVING COUNT(*) >= 20
        ORDER BY cnt DESC
    """)
    
    logger.info(f"處理 {len(stocks)} 支股票")
    total_records = 0
    
    for i, stock in enumerate(stocks, 1):
        code = stock['stock_code']
        
        try:
            # 獲取價格
            prices = db.execute_query("""
                SELECT trade_date, close_price, volume
                FROM tw_stock_prices 
                WHERE stock_code = %s 
                ORDER BY trade_date
            """, (code,))
            
            df = pd.DataFrame(prices)
            df['close_price'] = df['close_price'].astype(float)
            
            # 計算簡單移動平均
            df['ma5'] = df['close_price'].rolling(5).mean()
            df['ma20'] = df['close_price'].rolling(20).mean()
           
            # 寫入（逐筆，確保成功）
            count = 0
            for _, row in df.iterrows():
                if pd.notna(row['ma5']):
                    try:
                        db.execute_query("""
                            INSERT INTO technical_indicators 
                            (stock_code, calculation_date, ma5, ma20)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (code, row['trade_date'], 
                              float(row['ma5']), 
                              float(row['ma20']) if pd.notna(row['ma20']) else None))
                        count += 1
                    except:
                        pass
            
            total_records += count
            if i % 10 == 0:
                logger.info(f"{i}/{len(stocks)} - 已寫入{total_records}筆")
        
        except Exception as e:
            logger.error(f"{code}: {str(e)[:30]}")
    
    logger.info(f"✅ 完成 - 總計{total_records}筆")
    
finally:
    db.close()
