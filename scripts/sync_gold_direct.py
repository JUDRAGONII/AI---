"""
黃金價格數據同步（直接SQL連接版）
繞過DatabaseConnector問題
"""
import psycopg2
from psycopg2 import extras
import yfinance as yf
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

def sync_gold():
    """直接同步黃金數據"""
    print("=" * 60)
    print("💰 開始同步黃金價格（直接SQL）")
    print("=" * 60)
    
    # 連接資料庫
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    try:
        cursor = conn.cursor()
        
        # 獲取黃金數據
        print("📡 從yfinance獲取GC=F...")
        gold = yf.Ticker("GC=F")
        df = gold.history(period="1y")
        
        if df.empty:
            print("❌ 無法獲取數據")
            return 0
        
        print(f"✅ 獲取到 {len(df)} 筆數據")
        
        # 逐筆插入
        count = 0
        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO commodity_prices 
                    (commodity_code, commodity_name, trade_date, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (commodity_code, trade_date)
                    DO UPDATE SET close_price = EXCLUDED.close_price
                """, ('GOLD', '黃金', date.date(), float(row['Close']), int(row['Volume'])))
                count += 1
            except Exception as e:
                print(f"寫入失敗: {date.date()}")
                continue
        
        conn.commit()
        print(f"✅ 成功寫入 {count} 筆")
        
        # 驗證
        cursor.execute("SELECT COUNT(*) FROM commodity_prices WHERE commodity_code='GOLD'")
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
    result = sync_gold()
    print(f"\n🎉 完成！寫入 {result} 筆黃金數據")
