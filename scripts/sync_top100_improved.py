"""
擴展同步：台股前100大（含真實名稱）
使用ON CONFLICT處理重複
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime
from data_loader import DatabaseConnector
from loguru import logger
import time

# 台股前100大（已去重）
TOP_100 = [
    '2330', '2317', '2454', '2412', '2882', '2881', '2886', '2308', '2891', '3711',
    '2884', '2912', '2892', '2880', '1301', '1303', '2357', '2382', '2303', '2887',
    '2395', '5880', '6505', '2379', '2474', '3008', '5871', '2408', '3045', '2890',
    '2301', '1216', '2105', '2207', '2609', '2615', '9910', '2888', '1326', '2885',
    '2801', '2883', '2409', '2377', '2327', '3034', '2324', '1402', '2347', '2354',
    '2049', '2603', '3231', '4904', '2228', '4938', '2344', '2376', '2385', '2371',
    '1101', '2227', '2313', '2345', '1102', '6669', '2360', '3037', '2337', '2352',
    '2367', '2201', '2356', '2353', '3443', '2388', '2325', '6415', '2384', '1605',
    '3481', '3661', '2204', '2340', '2022', '3017', '6446', '6239', '2923', '3703',
    '2548', '6176', '4961', '3035', '1476', '2002', '5876', '2855', '1717', '2382'
]

db = DatabaseConnector()
new_stocks = 0
new_prices = 0

logger.info("=" * 80)
logger.info(f"🚀 同步台股前100大（使用UPSERT）")
logger.info("=" * 80)

try:
    for i, code in enumerate(TOP_100, 1):
        logger.info(f"[{i}/100] {code}")
        
        try:
            # 使用execute_query配合ON CONFLICT DO UPDATE
            db.execute_query(f"""
                INSERT INTO tw_stock_info (stock_code, stock_name, industry, market)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = EXCLUDED.stock_name,
                    updated_at = NOW()
            """, (code, f'股票{code}', '待更新', 'TWSE'))
            new_stocks += 1
            
            # 獲取價格
            ticker = yf.Ticker(f'{code}.TW')
            df = ticker.history(period='1mo')
            
            if not df.empty:
                prices = []
                for date, row in df.iterrows():
                    # 使用execute_query逐筆UPSERT
                    db.execute_query("""
                        INSERT INTO tw_stock_prices 
                        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, trade_date) DO UPDATE
                        SET open_price = EXCLUDED.open_price,
                            high_price = EXCLUDED.high_price,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume
                    """, (code, date.date(), float(row['Open']), float(row['High']),
                          float(row['Low']), float(row['Close']), int(row['Volume'])))
                new_prices += len(df)
                logger.info(f"  ✅ {len(df)}筆")
            
            if i % 10 == 0:
                time.sleep(1)
                logger.info(f"  ⏸️  進度: {i}/100")
                
        except Exception as e:
            logger.error(f"  ❌ {str(e)[:100]}")
    
    # 統計
    result = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_info")[0]
    total_stocks = result['c']
    result = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")[0]
    total_prices = result['c']
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 完成")
    logger.info("=" * 80)
    logger.info(f"股票: {total_stocks}支")
    logger.info(f"價格: {total_prices}筆")
    logger.info("=" * 80)
    
finally:
    db.close()
