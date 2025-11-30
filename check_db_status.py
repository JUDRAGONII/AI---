import psycopg2
import os
from datetime import datetime

def check_db():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=15432,
            database='quant_db',
            user='postgres',
            password='postgres'
        )
        cur = conn.cursor()
        
        # 1. 檢查黃金數據
        cur.execute("SELECT COUNT(*) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        gold_count = cur.fetchone()[0]
        print(f"Gold Data Count: {gold_count}")
        
        # 2. 檢查所有資料表
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables: {tables}")
        
        # 3. 檢查AI報告
        if 'ai_analysis_reports' in tables:
            cur.execute("SELECT COUNT(*) FROM ai_analysis_reports")
            report_count = cur.fetchone()[0]
            print(f"AI Reports Count: {report_count}")
            
            # 顯示最近一筆報告
            if report_count > 0:
                cur.execute("SELECT title, created_at FROM ai_analysis_reports ORDER BY created_at DESC LIMIT 1")
                print(f"Latest Report: {cur.fetchone()}")
        else:
            print("Table 'ai_analysis_reports' does not exist!")

        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_db()
