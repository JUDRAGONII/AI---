"""
簡化版技術指標計算 - 使用tw_stock_prices直接計算
不依賴technical_indicators表
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from data_loader import DatabaseConnector
from loguru import logger

def calculate_indicators(prices_df):
    """計算所有技術指標"""
    df = prices_df.copy()
    
    # MA
    df['ma5'] = df['close_price'].rolling(5).mean()
    df['ma10'] = df['close_price'].rolling(10).mean()
    df['ma20'] = df['close_price'].rolling(20).mean()
    
    # RSI
    delta = df['close_price'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp12 = df['close_price'].ewm(span=12, adjust=False).mean()
    exp26 = df['close_price'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp12 - exp26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['histogram'] = df['macd'] - df['signal']
    
    # 布林帶
    df['bb_middle'] = df['close_price'].rolling(20).mean()
    bb_std = df['close_price'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    return df

db = DatabaseConnector()

logger.info("開始計算技術指標（直接模式）")

try:
    # 獲取所有股票
    stocks = db.execute_query("SELECT DISTINCT stock_code FROM tw_stock_prices ORDER BY stock_code LIMIT 10")
    
    results = {}
    
    for stock in stocks:
        code = stock['stock_code']
        
        # 獲取價格數據
        prices = db.execute_query("""
            SELECT trade_date, close_price, volume
            FROM tw_stock_prices
            WHERE stock_code = %s
            ORDER BY trade_date
        """, (code,))
        
        if len(prices) < 26:
            continue
        
        df = pd.DataFrame(prices)
        df['close_price'] = df['close_price'].astype(float)
        
        # 計算指標
        df = calculate_indicators(df)
        
        # 取最新數據
        latest = df.iloc[-1]
        
        results[code] = {
            'ma5': float(latest['ma5']) if pd.notna(latest['ma5']) else None,
            'ma20': float(latest['ma20']) if pd.notna(latest['ma20']) else None,
            'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
            'macd': float(latest['macd']) if pd.notna(latest['macd']) else None,
        }
        
        logger.info(f"{code}: MA5={results[code]['ma5']:.2f}, RSI={results[code]['rsi']:.1f}")
    
    logger.info(f"✅ 完成 {len(results)} 支股票的技術指標計算")
    
    # 儲存結果到JSON
    import json
    with open('indicators_cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info("📁 結果已儲存到 indicators_cache.json")
    
finally:
    db.close()
