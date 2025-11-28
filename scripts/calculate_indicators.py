"""
階段3：計算技術指標
為所有股票計算MA, RSI, MACD等指標
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from data_loader import DatabaseConnector
from loguru import logger

def calculate_ma(prices, period):
    """計算移動平均"""
    return prices.rolling(window=period).mean()

def calculate_rsi(prices, period=14):
    """計算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    """計算MACD"""
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

db = DatabaseConnector()

logger.info("📊 開始計算技術指標")

try:
    # 獲取所有有價格數據的股票
    stocks = db.execute_query("""
        SELECT DISTINCT stock_code 
        FROM tw_stock_prices 
        ORDER BY stock_code
    """)
    
    logger.info(f"處理 {len(stocks)} 支股票")
    
    for i, stock in enumerate(stocks, 1):
        code = stock['stock_code']
        
        if i % 10 == 0:
            logger.info(f"進度: {i}/{len(stocks)}")
        
        try:
            # 獲取價格數據
            prices_data = db.execute_query("""
                SELECT trade_date, close_price 
                FROM tw_stock_prices 
                WHERE stock_code = %s 
                ORDER BY trade_date
            """, (code,))
            
            if len(prices_data) < 26:  # MACD需要至少26天
                continue
            
            df = pd.DataFrame(prices_data)
            df['close_price'] = df['close_price'].astype(float)
            
            # 計算指標
            df['ma5'] = calculate_ma(df['close_price'], 5)
            df['ma20'] = calculate_ma(df['close_price'], 20)
            df['ma60'] = calculate_ma(df['close_price'], 60)
            df['rsi'] = calculate_rsi(df['close_price'])
            df['macd'], df['signal'] = calculate_macd(df['close_price'])
            
            # 寫入資料庫
            for _, row in df.iterrows():
                if pd.notna(row['ma5']):  # 只寫入有效數據
                    db.execute_query("""
                        INSERT INTO technical_indicators 
                        (stock_code, calculation_date, ma_5, ma_20, ma_60, rsi_14, macd, macd_signal)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, calculation_date) DO UPDATE
                        SET ma_5 = EXCLUDED.ma_5,
                            ma_20 = EXCLUDED.ma_20,
                            ma_60 = EXCLUDED.ma_60,
                            rsi_14 = EXCLUDED.rsi_14,
                            macd = EXCLUDED.macd,
                            macd_signal = EXCLUDED.macd_signal
                    """, (code, row['trade_date'],
                          float(row['ma5']) if pd.notna(row['ma5']) else None,
                          float(row['ma20']) if pd.notna(row['ma20']) else None,
                          float(row['ma60']) if pd.notna(row['ma60']) else None,
                          float(row['rsi']) if pd.notna(row['rsi']) else None,
                          float(row['macd']) if pd.notna(row['macd']) else None,
                          float(row['signal']) if pd.notna(row['signal']) else None))
        
        except Exception as e:
            logger.error(f"{code}: {str(e)[:50]}")
    
    # 統計
    result = db.execute_query("SELECT COUNT(*) as c FROM technical_indicators")[0]
    logger.info(f"✅ 完成 - 技術指標: {result['c']}筆")
    
finally:
    db.close()
