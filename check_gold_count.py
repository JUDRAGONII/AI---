import psycopg2

def check_gold_data():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=15432,
            database='quant_db',
            user='postgres',
            password='postgres'
        )
        cur = conn.cursor()
        
        # 檢查黃金數據
        cur.execute("SELECT COUNT(*) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        gold_count = cur.fetchone()[0]
        print(f"黃金數據筆數: {gold_count}")
        
        # 檢查最新日期
        cur.execute("""
            SELECT trade_date, close_price 
            FROM commodity_prices 
            WHERE commodity_code = 'GOLD' 
            ORDER BY trade_date DESC LIMIT 1
        """)
        latest = cur.fetchone()
        if latest:
            print(f"最新日期: {latest[0]}, 價格: ${latest[1]}")
        
        # 檢查最舊日期
        cur.execute("""
            SELECT trade_date, close_price 
            FROM commodity_prices 
            WHERE commodity_code = 'GOLD' 
            ORDER BY trade_date ASC LIMIT 1
        """)
        oldest = cur.fetchone()
        if oldest:
            print(f"最舊日期: {oldest[0]}, 價格: ${oldest[1]}")
        
        conn.close()
        return gold_count
    except Exception as e:
        print(f"錯誤: {e}")
        return None

if __name__ == "__main__":
    count = check_gold_data()
    if count:
        print(f"\n✓ 資料庫中黃金數據: {count} 筆")
