"""
美股同步修正版 - 獨立錯誤處理
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

US_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'META', 'TSLA', 'BRK-B', 'JPM', 'JNJ',
    'V', 'WMT', 'PG', 'MA', 'HD',
    'DIS', 'PYPL', 'NFLX', 'ADBE', 'CRM',
    'CMCSA', 'PFE', 'KO', 'PEP', 'COST',
    'TMO', 'ABT', 'MRK', 'CSCO', 'NKE'
]

def sync_us_fixed():
    print("=" * 60)
    print("🇺🇸 美股同步（修正版 - 獨立錯誤處理）")
    print("=" * 60)
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    stock_count = 0
    price_count = 0
    
    for symbol in US_STOCKS:
        # 每支股票使用獨立連接和交易
        try:
            cursor = conn.cursor()
            print(f"處理 {symbol}...")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 寫入股票資訊
            try:
                cursor.execute("""
                    INSERT INTO us_stock_info 
                    (symbol, name, sector, industry, market_cap, country)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE
                    SET name = EXCLUDED.name,
                        sector = EXCLUDED.sector,
                        industry = EXCLUDED.industry,
                        market_cap = EXCLUDED.market_cap
                """, (
                    symbol,
                    info.get('longName', symbol),
                    info.get('sector', ''),
                    info.get('industry', ''),
                    info.get('marketCap', 0),
                    'US'
                ))
                stock_count += 1
            except Exception as e:
                print(f"  ⚠️  資訊寫入失敗: {str(e)[:40]}")
                conn.rollback()
                continue
            
            # 獲取價格數據
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                print(f"  ⚠️  無價格數據")
                conn.rollback()
                continue
            
            # 批次寫入價格
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO us_stock_prices 
                        (symbol, trade_date, open_price, high_price, 
                         low_price, close_price, volume, adj_close)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume
                    """, (
                        symbol,
                        date.date(),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        int(row['Volume']),
                        float(row['Close'])
                    ))
                    price_count += 1
                except:
                    continue
            
            conn.commit()  # 每支股票獨立commit
            print(f"  ✅ {symbol} 完成 ({len(hist)}筆)")
            
        except Exception as e:
            print(f"  ❌ {symbol} 失敗: {str(e)[:40]}")
            conn.rollback()
            continue
        finally:
            if cursor:
                cursor.close()
    
    print(f"\n✅ 成功同步 {stock_count} 支美股")
    print(f"✅ 成功寫入 {price_count} 筆價格")
    
    conn.close()
    return stock_count

if __name__ == '__main__':
    result = sync_us_fixed()
    print(f"\n🎉 完成！同步 {result} 支美股")
