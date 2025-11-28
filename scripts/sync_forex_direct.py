"""
美元台幣匯率同步（直接SQL）
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

def sync_forex():
    """同步匯率"""
    print("=" * 60)
    print("💱 開始同步美元台幣匯率")
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
        
        print("📡 從yfinance獲取TWD=X...")
        ticker = yf.Ticker("TWD=X")
        df = ticker.history(period="1y")
        
        if df.empty:
            print("❌ 無法獲取數據")
            return 0
        
        print(f"✅ 獲取到 {len(df)} 筆")
        
        count = 0
        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO exchange_rates 
                    (base_currency, quote_currency, trade_date, rate)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (base_currency, quote_currency, trade_date)
                    DO UPDATE SET rate = EXCLUDED.rate
                """, ('USD', 'TWD', date.date(), float(row['Close'])))
                count += 1
            except:
                continue
        
        conn.commit()
        print(f"✅ 成功寫入 {count} 筆")
        
        cursor.execute("SELECT COUNT(*) FROM exchange_rates WHERE base_currency='USD'")
        total = cursor.fetchone()[0]
        print(f"📊 資料庫總計: {total} 筆")
        
        return count
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    result = sync_forex()
    print(f"\n🎉 完成！寫入 {result} 筆匯率數據")
