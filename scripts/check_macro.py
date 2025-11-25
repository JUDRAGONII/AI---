import sys
from pathlib import Path
import psycopg2

# 添加專案根目錄
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_CONFIG

def check_macro_count():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM macro_indicators")
        count = cur.fetchone()[0]
        
        print(f"✅ Macro count: {count}")
        
        if count > 0:
            cur.execute("SELECT indicator_type, COUNT(*) FROM macro_indicators GROUP BY indicator_type")
            rows = cur.fetchall()
            for row in rows:
                print(f"   - {row[0]}: {row[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

if __name__ == '__main__':
    check_macro_count()
