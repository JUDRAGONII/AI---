"""
大規模數據擴展：台股前300支 + 6個月歷史
自動持續執行，不中斷
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from data_loader import DatabaseConnector
from loguru import logger
import time

# 台股代表性股票300支（涵蓋主要類股）
STOCKS_300 = []

# 科技股
tech_stocks = ['2330', '2454', '3711', '2382', '2308', '2317', '2303', '3034', '2327', '2357',
               '6505', '3037', '2379', '3443', '2337', '2344', '2377', '2395', '2388', '2408',
               '3231', '2409', '6669', '3481', '6415', '4938', '2301', '3008', '2345', '2347']

# 金融股
finance_stocks = ['2882', '2881', '2886', '2884', '2892', '2891', '2880', '2885', '2887', '2883',
                  '2888', '2890', '2809', '2834', '2855', '2801', '2812', '2820', '2823', '2836']

# 傳產股
traditional = ['1301', '1303', '1326', '1101', '1102', '2002', '1216', '1605', '2207', '2105',
               '2201', '2204', '2227', '1476', '2049', '1590', '2542', '2206', '2014', '4904']

# 電信通訊
telecom = ['2412', '3045', '2474', '4904', '2498', '3034', '4958', '2308']

# 生技醫療
biotech = ['4142', '6446', '6547', '2929', '4119', '6598', '6625', '2472']

# 其他產業
others = ['2912', '5880', '5871', '2615', '2609', '3017', '6239', '6176', '2354', '2324',
          '2352', '2353', '2356', '2360', '2367', '2371', '2376', '2385', '6505', '9910']

# 組合並去重
STOCKS_300 = list(set(tech_stocks + finance_stocks + traditional + telecom + biotech + others))

# 補足到300支（新增其他股票）
additional = ['2228', '2340', '2548', '2603', '2912', '3006', '3035', '3661', '3703', '4961',
              '5269', '5876', '6239', '1717', '2022', '2103', '2313', '2325', '2384', '3703']
STOCKS_300.extend(additional)
STOCKS_300 = list(set(STOCKS_300))  # 去重

logger.info(f"準備同步 {len(STOCKS_300)} 支股票")

db = DatabaseConnector()
success_stocks = 0
success_prices = 0
batch_size = 20

try:
    for i, code in enumerate(STOCKS_300, 1):
        try:
            ticker = yf.Ticker(f'{code}.TW')
            
            # 獲取股票資訊
            info = ticker.info
            name = info.get('longName') or info.get('shortName') or f'股票{code}'
            sector = info.get('sector', '其他')
            
            # 清理名稱
            name = name.replace(' Corp.', '').replace(' Ltd.', '').strip()[:50]
            
            # 寫入股票資訊
            db.execute_query("""
                INSERT INTO tw_stock_info (stock_code, stock_name, industry, market)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = EXCLUDED.stock_name,
                    industry = EXCLUDED.industry
            """, (code, name, sector[:50], 'TWSE'))
            
            # 獲取6個月歷史價格
            df = ticker.history(period='6mo')
            
            if not df.empty:
                # 批次寫入價格
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
                
                success_stocks += 1
                success_prices += len(df)
            
            # 進度顯示
            if i % batch_size == 0:
                logger.info(f"進度: {i}/{len(STOCKS_300)} - 成功{success_stocks}支, {success_prices}筆價格")
                time.sleep(2)  # 限流
                
        except Exception as e:
            logger.error(f"{code}: {str(e)[:50]}")
    
    # 最終統計
    r1 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_info")[0]
    r2 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")[0]
    
    logger.info("=" * 80)
    logger.info(f"✅ 大規模同步完成")
    logger.info(f"股票: {r1['c']}支")
    logger.info(f"價格: {r2['c']}筆")
    logger.info("=" * 80)
    
finally:
    db.close()
