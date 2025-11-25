import sys
from pathlib import Path
import psycopg2

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import DATABASE_CONFIG

def get_backfill_status():
    """查詢當前資料庫回溯狀態"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        print("=" * 80)
        print("資料庫回溯情形報告")
        print("=" * 80)
        print()
        
        # 查詢各表資料筆數
        tables = {
            'gold_prices': '黃金價格',
            'exchange_rates': '匯率資料',
            'macro_indicators': '宏觀經濟',
            'tw_stock_prices': '台股價格',
            'us_stock_prices': '美股價格',
            'financial_news': '金融新聞',
            'tw_stock_info': '台股基本資料',
            'us_stock_info': '美股基本資料'
        }
        
        for table, desc in tables.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            
            # 獲取日期範圍
            date_col = 'trade_date' if 'price' in table else ('release_date' if 'macro' in table else ('published_at' if 'news' in table else 'data_date'))
            
            if count > 0 and 'info' not in table:
                try:
                    cur.execute(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table}")
                    min_date, max_date = cur.fetchone()
                    print(f"{desc:15} | {count:>10,} 筆 | {min_date} ~ {max_date}")
                except:
                    print(f"{desc:15} | {count:>10,} 筆")
            else:
                print(f"{desc:15} | {count:>10,} 筆")
        
        print()
        print("=" * 80)
        print("同步狀態")
        print("=" * 80)
        
        cur.execute("""
            SELECT data_source, source_identifier, sync_status, 
                   earliest_date, latest_date, total_records, updated_at
            FROM sync_status
            ORDER BY updated_at DESC
        """)
        
        for row in cur.fetchall():
            print(f"\n資料來源: {row[0]} / {row[1]}")
            print(f"  狀態: {row[2]}")
            print(f"  筆數: {row[5]:,}")
            print(f"  日期範圍: {row[3]} ~ {row[4]}")
            print(f"  更新時間: {row[6]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

if __name__ == '__main__':
    get_backfill_status()
