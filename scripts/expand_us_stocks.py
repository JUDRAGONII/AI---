"""
擴展美股數據 - 從10支擴展到30支
補充完整前30支美股
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# 美股前30支（已有10支：AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, JPM, V, WMT）
# 新增20支
NEW_US_STOCKS = [
    'PG', 'MA', 'HD', 'DIS', 'PYPL', 'NFLX', 'ADBE', 'CRM', 'CMCSA', 'PFE',
    'KO', 'PEP', 'COST', 'TMO', 'ABT', 'MRK', 'CSCO', 'NKE', 'INTC', 'AMD'
]

def expand_us_stocks():
    print("=" * 60)
    print("🇺🇸 擴展美股數據：10支 → 30支")
    print("=" * 60)
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = conn.cursor()
    
    # 檢查現有
    cursor.execute("SELECT COUNT(*) FROM us_stock_info")
    existing = cursor.fetchone()[0]
    print(f"現有美股：{existing}支")
    
    stock_count = 0
    price_count = 0
    
    for symbol in NEW_US_STOCKS:
        try:
            print(f"處理 {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 寫入股票資訊（使用company_name）
            cursor.execute("""
                INSERT INTO us_stock_info 
                (symbol, company_name, sector, industry, market_cap)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE
                SET company_name = EXCLUDED.company_name
            """, (symbol, info.get('longName', symbol), info.get('sector', ''), info.get('industry', ''), info.get('marketCap', 0)))
            
            stock_count += 1
            
            # 獲取1個月價格
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
            print(f"  ✅ {symbol}: {len(hist)}筆")
            
        except Exception as e:
            print(f"  ❌ {symbol}: {str(e)[:30]}")
            conn.rollback()
            continue
    
    print(f"\n✅ 新增 {stock_count} 支美股")
    print(f"✅ 新增 {price_count} 筆價格")
    
    # 驗證總數
    cursor.execute("SELECT COUNT(*) FROM us_stock_info")
    total_stocks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM us_stock_prices")
    total_prices = cursor.fetchone()[0]
    
    print(f"📊 資料庫總計: {total_stocks}支美股、{total_prices}筆價格")
    
    cursor.close()
    conn.close()
    
    return stock_count

if __name__ == '__main__':
    result = expand_us_stocks()
    print(f"\n🎉 完成！新增 {result} 支美股")
