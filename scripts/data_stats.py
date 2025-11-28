"""
創建完整的數據統計報告
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import DatabaseConnector
from datetime import datetime

db = DatabaseConnector()

print("=" * 80)
print(f"📊 數據統計報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

try:
    # 台股統計
    print("\n【台股數據】")
    r1 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_info")[0]
    print(f"  股票總數: {r1['c']}支")
    
    r2 = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")[0]
    print(f"  價格記錄: {r2['c']:,}筆")
    
    r3 = db.execute_query("""
        SELECT COUNT(DISTINCT stock_code) as stocks, 
               MIN(trade_date) as earliest, 
               MAX(trade_date) as latest
        FROM tw_stock_prices
    """)[0]
    print(f"  有價格股票: {r3['stocks']}支")
    print(f"  數據期間: {r3['earliest']} 至 {r3['latest']}")
    
    # 美股統計
    print("\n【美股數據】")
    r4 = db.execute_query("SELECT COUNT(*) as c FROM us_stock_info")[0]
    print(f"  股票總數: {r4['c']}支")
    
    r5 = db.execute_query("SELECT COUNT(*) as c FROM us_stock_prices")[0]
    print(f"  價格記錄: {r5['c']:,}筆")
    
    # 系統配置
    print("\n【系統配置】")
    r6 = db.execute_query("SELECT COUNT(*) as c FROM system_config")[0]
    print(f"  配置項目: {r6['c']}個")
    
    r7 = db.execute_query("SELECT COUNT(*) as c FROM sync_status")[0]
    print(f"  同步記錄: {r7['c']}筆")
    
    # 前10名股票
    print("\n【熱門股票（按價格筆數）】")
    top = db.execute_query("""
        SELECT stock_code, COUNT(*) as cnt
        FROM tw_stock_prices
        GROUP BY stock_code
        ORDER BY cnt DESC
        LIMIT 10
    """)
    for i, row in enumerate(top, 1):
        print(f"  {i}. {row['stock_code']}: {row['cnt']}筆")
    
    print("\n" + "=" * 80)
    print(f"✅ 統計完成")
    print("=" * 80)
    
finally:
    db.close()
