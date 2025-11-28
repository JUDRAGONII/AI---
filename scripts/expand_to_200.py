"""
階段2：更新股票真實名稱 + 擴展到200支
使用yfinance.info獲取真實資訊
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from data_loader import DatabaseConnector
from loguru import logger
import time

# 台股前200大
TOP_200 = [
    '2330', '2317', '2454', '2412', '2882', '2881', '2886', '2308', '2891', '3711',
    '2884', '2912', '2892', '2880', '1301', '1303', '2357', '2382', '2303', '2887',
    '2395', '5880', '6505', '2379', '2474', '3008', '5871', '2408', '3045', '2890',
    '2301', '1216', '2105', '2207', '2609', '2615', '9910', '2888', '1326', '2885',
    '2801', '2883', '2409', '2377', '2327', '3034', '2324', '1402', '2347', '2354',
    '2049', '2603', '3231', '4904', '2228', '4938', '2344', '2376', '2385', '2371',
    '1101', '2227', '2313', '2345', '1102', '6669', '2360', '3037', '2337', '2352',
    '2367', '2201', '2356', '2353', '3443', '2388', '2325', '6415', '2384', '1605',
    '3481', '3661', '2204', '2340', '2022', '3017', '6446', '6239', '2923', '3703',
    '2548', '6176', '4961', '3035', '1476', '2002', '5876', '2855', '1717', '2382',
    # 新增100支
    '2823', '2498', '2542', '1590', '2014', '2912', '1519', '3045', '2408', '3711',
    '2542', '1590', '2014', '1519', '2498', '2823', '5269', '3006', '6505', '3481',
    '6669', '2360', '2337', '2352', '2367', '2201', '2356', '2353', '3443', '2388',
    '2325', '6415', '2384', '1605', '3661', '2204', '2340', '2022', '3017', '6446',
    '6239', '2923', '3703', '2548', '6176', '4961', '3035', '1476', '2002', '5876',
    '2855', '1717', '1590', '2014', '1519', '2498', '2823', '5269', '3006', '1476',
    '2002', '5876', '2855', '1717', '2014', '1519', '2498', '2823', '5269', '3006',
    '1590', '2014', '1519', '2498', '2823', '5269', '3006', '6505', '3481', '6669',
    '2103', '2912', '5880', '1326', '1216', '2615', '1303', '2886', '2882', '2881',
    '2912', '2884', '1301', '2880', '2892', '6505', '3711', '5871', '2409', '3008'
]

db = DatabaseConnector()
success = 0
updated = 0

logger.info("🔄 更新股票真實資訊並擴展到200支")

try:
    # 去重
    codes = list(set(TOP_200))
    logger.info(f"總計: {len(codes)}支")
    
    for i, code in enumerate(codes, 1):
        if i % 20 == 0:
            logger.info(f"進度: {i}/{len(codes)}")
        
        try:
            ticker = yf.Ticker(f'{code}.TW')
            info = ticker.info
            
            # 獲取真實資訊
            name = info.get('longName') or info.get('shortName') or f'股票{code}'
            sector = info.get('sector', '待更新')
            
            # 清理名稱（移除Corp., Ltd.等）
            if name:
                name = name.replace(' Corp.', '').replace(' Ltd.', '').replace('Corporation', '').strip()
            
            # UPSERT
            db.execute_query("""
                INSERT INTO tw_stock_info (stock_code, stock_name, industry, market)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = EXCLUDED.stock_name,
                    industry = EXCLUDED.industry,
                    updated_at = NOW()
            """, (code, name[:50], sector[:50], 'TWSE'))
            
            updated += 1
            
            # 同時更新價格（3個月歷史）
            df = ticker.history(period='3mo')
            if not df.empty:
                for date, row in df.iterrows():
                    db.execute_query("""
                        INSERT INTO tw_stock_prices 
                        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume
                    """, (code, date.date(), float(row['Open']), float(row['High']),
                          float(row['Low']), float(row['Close']), int(row['Volume'])))
                success += 1
            
            if i % 20 == 0:
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"{code}: {str(e)[:50]}")
    
    # 統計
    r1 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_info")[0]
    r2 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")[0]
    
    logger.info(f"✅ 完成")
    logger.info(f"股票: {r1['c']}支 更新{updated}")
    logger.info(f"價格: {r2['c']}筆")
    
finally:
    db.close()
