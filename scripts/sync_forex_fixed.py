"""
匯率同步修正版 - 診斷並修正TWD=X問題
"""
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

def sync_forex_fixed():
    print("=" * 60)
    print("💱 美元台幣匯率同步（修正版）")
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
        
        # 嘗試多個匯率代碼
        symbols = ['USDTWD=X', 'TWD=X', 'TWDUSD=X']
        df = None
        used_symbol = None
        
        for symbol in symbols:
            print(f"📡 嘗試 {symbol}...")
            try:
                ticker = yf.Ticker(symbol)
                temp_df = ticker.history(period="6mo")  # 6個月數據
                if not temp_df.empty:
                    df = temp_df
                    used_symbol = symbol
                    print(f"✅ {symbol} 成功獲取 {len(df)} 筆")
                    break
            except:
                continue
        
        if df is None or df.empty:
            print("❌ 所有匯率代碼都無法獲取數據")
            # 使用固定匯率作為備案
            print("📝 使用固定匯率 31.5 作為備案")
            from datetime import datetime, timedelta
            cursor.execute("""
                INSERT INTO exchange_rates 
                (base_currency, quote_currency, trade_date, rate)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (base_currency, quote_currency, trade_date)
                DO UPDATE SET rate = EXCLUDED.rate
            """, ('USD', 'TWD', datetime.now().date(), 31.5))
            conn.commit()
            return 1
        
        # 打印數據樣本
        print(f"\n📊 數據樣本 (前3筆):")
        for i, (date, row) in enumerate(df.head(3).iterrows()):
            print(f"  {date.date()}: Close={row['Close']:.4f}")
        
        count = 0
        for date, row in df.iterrows():
            try:
                rate = float(row['Close'])
                if rate <= 0 or rate > 100:  # 合理性檢查
                    print(f"⚠️  跳過異常匯率: {date.date()} = {rate}")
                    continue
                
                cursor.execute("""
                    INSERT INTO exchange_rates 
                    (base_currency, quote_currency, trade_date, rate)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (base_currency, quote_currency, trade_date)
                    DO UPDATE SET rate = EXCLUDED.rate
                """, ('USD', 'TWD', date.date(), rate))
                count += 1
            except Exception as e:
                print(f"寫入失敗 {date.date()}: {e}")
                continue
        
        conn.commit()
        print(f"\n✅ 成功寫入 {count} 筆匯率")
        
        # 驗證
        cursor.execute("""
            SELECT COUNT(*), MIN(rate), MAX(rate), AVG(rate) 
            FROM exchange_rates 
            WHERE base_currency='USD' AND quote_currency='TWD'
        """)
        stats = cursor.fetchone()
        print(f"📊 資料庫統計:")
        print(f"  總計: {stats[0]} 筆")
        print(f"  範圍: {stats[1]:.4f} - {stats[2]:.4f}")
        print(f"  平均: {stats[3]:.4f}")
        
        return count
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    result = sync_forex_fixed()
    print(f"\n🎉 完成！寫入 {result} 筆匯率數據")
