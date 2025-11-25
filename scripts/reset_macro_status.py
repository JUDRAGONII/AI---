import sys
from pathlib import Path
import psycopg2

# 添加專案根目錄
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_CONFIG

def reset_macro_status():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        # 刪除 macro 的同步狀態
        cur.execute("DELETE FROM sync_status WHERE data_source = 'macro'")
        deleted = cur.rowcount
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ 已清除 {deleted} 筆 macro 同步狀態，Phase 2 將會重新執行。")
        
    except Exception as e:
        print(f"❌ 清除失敗: {e}")

if __name__ == '__main__':
    reset_macro_status()
