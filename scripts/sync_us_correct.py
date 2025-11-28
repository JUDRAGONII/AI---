"""
美股同步正確版 - 使用company_name欄位
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

US_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'WMT']

def sync_us_correct():
    print("🇺🇸 美股同步（正確版 - company_name）")
    
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
        try:
            cursor = conn.cursor()
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 使用company_name欄位
            cursor.execute("""
                INSERT INTO us_stock_info 
                (symbol, company_name, sector, industry, market_cap)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE
                SET company_name = EXCLUDED.company_name
            """, (symbol, info.get('longName', symbol), info.get('sector', ''), info.get('industry', ''), info.get('marketCap', 0)))
            
            stock_count += 1
            
            hist = ticker.history(period="1mo")
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO us_stock_prices 
                        (symbol, trade_date, close_price, volume)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (symbol, trade_date) DO UPDATE
                        SET close_price = EXCLUDED.close_price
                    """, (symbol, date.date(), float(row['Close']), int(row['Volume'])))
                    price_count += 1
                except:
                    continue
            
            conn.commit()
            print(f"✅ {symbol}: {len(hist)}筆")
        except Exception as e:
            print(f"❌ {symbol}: {str(e)[:30]}")
            conn.rollback()
    
    print(f"\n✅ 同步 {stock_count} 支, {price_count} 筆價格")
    conn.close()
    return stock_count

if __name__ == '__main__':
    sync_us_correct()
