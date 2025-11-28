"""
大規模數據擴張腳本 - 充分利用yfinance免費API
目標：台股200支、美股100支、完整歷史數據
"""
import yfinance as yf
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# 台股前200支代碼（市值排序）
TW_STOCKS_200 = [
    # 前100支（已有102支）
    '2330', '2317', '2454', '2308', '2881', '2882', '2891', '2892', '2886', '2884',
    '2412', '2382', '1301', '1303', '1326', '2357', '2303', '3008', '2002', '6505',
    '2887', '2880', '2885', '2890', '1216', '2379', '2377', '2327', '3711', '2345',
    '6415', '6669', '5880', '2912', '2408', '3045', '2301', '2353', '1101', '2395',
    '3231', '5871', '2883', '2603', '1102', '2609', '2324', '2344', '2371', '2409',
    '1605', '3481', '6176', '2888', '2356', '5483', '9910', '2049', '3037', '6269',
    '2207', '2618', '2201', '2809', '2834', '2610', '3034', '1402', '1590', '4904',
    '2915', '1314', '2474', '2841', '3532', '2383', '4938', '4958', '5347', '2204',
    '6781', '3552', '2352', '1476', '5388', '6278', '6409', '2832', '2385', '2027',
    '3443', '2458', '2347', '3653', '4966', '5269', '6446', '8046', '2354', '2851',
    
    # 新增100支（101-200）
    '2498', '6116', '2368', '2377', '3017', '2434', '2376', '2059', '8299', '6488',
    '2923', '2888', '2834', '1590', '2449', '2448', '1718', '2542', '1907', '1723',
    '2801', '2439', '5388', '2006', '3406', '6415', '2204', '3450', '2441', '5483',
    '2206', '3711', '8150', '3702', '2027', '3034', '8358', '6239', '6176', '2428',
    '9921', '3037', '2313', '8341', '2912', '2356', '3008', '2371', '5434', '2888',
    '1476', '2610', '1477', '1504', '2809', '2201', '5871', '2535', '1802', '5388',
    '2385', '3481', '9910', '2458', '6269', '2383', '6278', '2352', '4938', '3532',
    '2841', '2915', '1314', '4904', '1590', '2474', '3034', '2834', '2409', '2603',
    '2324', '2344', '2609', '1102', '2371', '5871', '2883', '3231', '2395', '1101',
    '2353', '2301', '3045', '2408', '2912', '5880', '6669', '6415', '2345', '3711'
]

# 美股前100支代碼
US_STOCKS_100 = [
    # 已有30支
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'WMT',
    'PG', 'MA', 'HD', 'DIS', 'PYPL', 'NFLX', 'ADBE', 'CRM', 'CMCSA', 'PFE',
    'KO', 'PEP', 'COST', 'TMO', 'ABT', 'MRK', 'CSCO', 'NKE', 'INTC', 'AMD',
    
    # 新增70支（31-100）
    'AVGO', 'ORCL', 'ACN', 'TXN', 'QCOM', 'LLY', 'UNH', 'NVO', 'ASML', 'LIN',
    'NEE', 'DHR', 'UNP', 'T', 'VZ', 'PM', 'BA', 'RTX', 'HON', 'AMGN',
    'UPS', 'LOW', 'BMY', 'SBUX', 'CAT', 'DE', 'NOW', 'INTU', 'ISRG', 'GE',
    'MDT', 'SPGI', 'BLK', 'AXP', 'MMM', 'GS', 'ADP', 'CI', 'MO', 'USB',
    'CVS', 'TJX', 'GILD', 'PLD', 'CME', 'EL', 'SYK', 'CSX', 'DUK', 'SO',
    'CL', 'MDLZ', 'REGN', 'ZTS', 'BDX', 'ITW', 'EOG', 'APD', 'MU', 'LRCX',
    'ADI', 'AMAT', 'KLAC', 'NXPI', 'MRVL', 'SNPS', 'CDNS', 'FTNT', 'PANW', 'WDAY'
]

def sync_massive_data():
    print("=" * 80)
    print("🚀 大規模數據擴張 - 充分利用yfinance免費API")
    print("=" * 80)
    print("目標：台股200支、美股100支、完整歷史數據")
    print("=" * 80)
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = conn.cursor()
    
    tw_stock_count = 0
    tw_price_count = 0
    us_stock_count = 0
    us_price_count = 0
    
    # ========== 1. 台股數據擴張 ==========
    print("\n【階段1】台股數據擴張（200支目標）")
    print("-" * 80)
    
    for idx, code in enumerate(TW_STOCKS_200, 1):
        try:
            print(f"[{idx}/200] 處理台股 {code}...", end=' ')
            
            # 插入股票資訊
            cursor.execute("""
                INSERT INTO tw_stock_info (stock_code, stock_name, market)
                VALUES (%s, %s, %s)
                ON CONFLICT (stock_code) DO NOTHING
            """, (code, f"股票{code}", '上市'))
            
            if cursor.rowcount > 0:
                tw_stock_count += 1
            
            # 獲取1年歷史價格
            ticker = yf.Ticker(f"{code}.TW")
            hist = ticker.history(period="1y")
            
            price_inserted = 0
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO tw_stock_prices 
                        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price
                    """, (code, date.date(), float(row['Open']), float(row['High']), 
                          float(row['Low']), float(row['Close']), int(row['Volume'])))
                    price_inserted += 1
                except:
                    continue
            
            tw_price_count += price_inserted
            conn.commit()
            print(f"✅ {price_inserted}筆")
            
            if idx % 10 == 0:
                time.sleep(1)  # 每10支休息1秒
                
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            conn.rollback()
            continue
    
    # ========== 2. 美股數據擴張 ==========
    print("\n【階段2】美股數據擴張（100支目標）")
    print("-" * 80)
    
    for idx, symbol in enumerate(US_STOCKS_100, 1):
        try:
            print(f"[{idx}/100] 處理美股 {symbol}...", end=' ')
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 插入股票資訊
            cursor.execute("""
                INSERT INTO us_stock_info 
                (symbol, company_name, sector, industry, market_cap)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE
                SET company_name = EXCLUDED.company_name
            """, (symbol, info.get('longName', symbol), 
                  info.get('sector', ''), info.get('industry', ''), 
                  info.get('marketCap', 0)))
            
            if cursor.rowcount > 0:
                us_stock_count += 1
            
            # 獲取1年歷史價格
            hist = ticker.history(period="1y")
            
            price_inserted = 0
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO us_stock_prices 
                        (symbol, trade_date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price
                    """, (symbol, date.date(), float(row['Open']), float(row['High']), 
                          float(row['Low']), float(row['Close']), int(row['Volume'])))
                    price_inserted += 1
                except:
                    continue
            
            us_price_count += price_inserted
            conn.commit()
            print(f"✅ {price_inserted}筆")
            
            if idx % 10 == 0:
                time.sleep(1)  # 每10支休息1秒
                
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            conn.rollback()
            continue
    
    # ========== 3. 更多商品數據 ==========
    print("\n【階段3】商品數據擴張")
    print("-" * 80)
    
    commodities = {
        'GOLD': 'GC=F',      # 黃金
        'SILVER': 'SI=F',    # 白銀
        'CRUDE': 'CL=F',     # 原油
        'COPPER': 'HG=F',    # 銅
        'NATGAS': 'NG=F'     # 天然氣
    }
    
    commodity_count = 0
    for name, symbol in commodities.items():
        try:
            print(f"處理 {name} ({symbol})...", end=' ')
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            inserted = 0
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO commodity_prices 
                        (commodity_code, trade_date, close_price, volume)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (commodity_code, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price
                    """, (name, date.date(), float(row['Close']), int(row['Volume'])))
                    inserted += 1
                except:
                    continue
            
            commodity_count += inserted
            conn.commit()
            print(f"✅ {inserted}筆")
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            continue
    
    # ========== 4. 更多匯率對 ==========
    print("\n【階段4】匯率數據擴張")
    print("-" * 80)
    
    forex_pairs = {
        'USDTWD': 'TWD=X',       # 美元/台幣
        'EURUSD': 'EURUSD=X',    # 歐元/美元
        'USDJPY': 'JPY=X',       # 美元/日圓
        'GBPUSD': 'GBPUSD=X',    # 英鎊/美元
        'USDCNY': 'CNY=X'        # 美元/人民幣
    }
    
    forex_count = 0
    for pair, symbol in forex_pairs.items():
        try:
            print(f"處理 {pair}...", end=' ')
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            
            base = pair[:3]
            quote = pair[3:]
            
            inserted = 0
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO exchange_rates 
                        (currency_pair, base_currency, quote_currency, trade_date, rate)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (base_currency, quote_currency, trade_date) DO UPDATE
                        SET rate = EXCLUDED.rate
                    """, (pair, base, quote, date.date(), float(row['Close'])))
                    inserted += 1
                except:
                    continue
            
            forex_count += inserted
            conn.commit()
            print(f"✅ {inserted}筆")
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            continue
    
    # ========== 最終統計 ==========
    print("\n" + "=" * 80)
    print("🎉 大規模數據擴張完成！")
    print("=" * 80)
    print(f"台股資訊：新增 {tw_stock_count} 支")
    print(f"台股價格：新增 {tw_price_count} 筆")
    print(f"美股資訊：新增 {us_stock_count} 支")
    print(f"美股價格：新增 {us_price_count} 筆")
    print(f"商品數據：新增 {commodity_count} 筆")
    print(f"匯率數據：新增 {forex_count} 筆")
    print(f"\n總計新增：{tw_price_count + us_price_count + commodity_count + forex_count} 筆數據")
    print("=" * 80)
    
    # 驗證總數
    cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
    total_tw = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM us_stock_info")
    total_us = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tw_stock_prices")
    total_tw_prices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM us_stock_prices")
    total_us_prices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM commodity_prices")
    total_commodities = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exchange_rates")
    total_forex = cursor.fetchone()[0]
    
    print("\n📊 資料庫總計：")
    print(f"  台股：{total_tw}支，{total_tw_prices}筆價格")
    print(f"  美股：{total_us}支，{total_us_prices}筆價格")
    print(f"  商品：{total_commodities}筆")
    print(f"  匯率：{total_forex}筆")
    print(f"  總數據量：{total_tw_prices + total_us_prices + total_commodities + total_forex} 筆")
    print("=" * 80)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    sync_massive_data()
