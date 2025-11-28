"""
匯率同步正確版 - 填充currency_pair欄位
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

def sync_forex_correct():
    print("💱 美元台幣匯率同步（正確版）")
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = conn.cursor()
    
    # 嘗試多個代碼
    for symbol in ['USDTWD=X', 'TWD=X']:
        print(f"嘗試 {symbol}...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo")
        
        if not df.empty:
            print(f"✅ 獲取 {len(df)} 筆")
            count = 0
            
            for date, row in df.iterrows():
                try:
                    rate = float(row['Close'])
                    if 20 < rate < 40:  # 合理範圍
                        cursor.execute("""
                            INSERT INTO exchange_rates 
                            (trade_date, currency_pair, base_currency, quote_currency, rate)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (base_currency, quote_currency, trade_date)
                            DO UPDATE SET rate = EXCLUDED.rate
                        """, (date.date(), 'USDTWD', 'USD', 'TWD', rate))
                        count += 1
                except Exception as e:
                    print(f"寫入失敗: {e}")
                    continue
            
            conn.commit()
            print(f"✅ 寫入 {count} 筆")
            cursor.close()
            conn.close()
            return count
    
    print("❌ 所有代碼都失敗")
    cursor.close()
    conn.close()
    return 0

if __name__ == '__main__':
    sync_forex_correct()
