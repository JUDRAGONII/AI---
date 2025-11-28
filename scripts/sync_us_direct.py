"""
美股前30支同步（直接SQL）
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

def sync_us():
    """同步美股"""
    print("=" * 60)
    print("🇺🇸 開始同步美股前30支")
    print("=" * 60)
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    try:
        cursor = conn.cursor()
        stock_count = 0
        price_count = 0
        
        for symbol in US_STOCKS:
            try:
                print(f"處理 {symbol}...")
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 寫入股票資訊
                cursor.execute("""
                    INSERT INTO us_stock_info 
                    (stock_code, stock_name, industry, market)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (stock_code) DO UPDATE
                    SET stock_name = EXCLUDED.stock_name
                """, (symbol, info.get('longName', symbol), info.get('industry', ''), 'US'))
                stock_count += 1
                
                # 獲取3個月價格
                hist = ticker.history(period="3mo")
                
                for date, row in hist.iterrows():
                    try:
                        cursor.execute("""
                            INSERT INTO us_stock_prices 
                            (stock_code, trade_date, close_price, volume)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (stock_code, trade_date) DO UPDATE
                            SET close_price = EXCLUDED.close_price
                        """, (symbol, date.date(), float(row['Close']), int(row['Volume'])))
                        price_count += 1
                    except:
                        continue
                
                print(f"  ✅ {symbol}")
                
            except Exception as e:
                print(f"  ❌ {symbol}: {str(e)[:30]}")
                continue
        
        conn.commit()
        print(f"\n✅ 成功同步 {stock_count} 支美股")
        print(f"✅ 成功寫入 {price_count} 筆價格")
        
        return stock_count
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    result = sync_us()
    print(f"\n🎉 完成！同步 {result} 支美股")
