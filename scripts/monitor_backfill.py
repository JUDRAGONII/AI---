"""
即時監控資料回溯進度
每 2 秒查詢一次資料庫筆數
"""
import time
import psycopg2
import sys
from datetime import datetime

# 資料庫配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 15432,
    'database': 'financial_data',
    'user': 'postgres',
    'password': '0824-003-a-8-Po'
}

def monitor():
    print("=" * 100)
    print("📊 資料回溯即時監控 (完整模式)")
    print("=" * 100)
    print(f"{'時間':<10} | {'黃金':<8} | {'匯率':<8} | {'宏觀':<8} | {'台股':<8} | {'美股':<8} | {'新聞':<8}")
    print("-" * 100)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        last_counts = {'gold': 0, 'rate': 0, 'macro': 0, 'tw': 0, 'us': 0, 'news': 0}
        
        # 持續監控
        while True:
            cur.execute("SELECT COUNT(*) FROM gold_prices")
            gold = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM exchange_rates")
            rate = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM macro_indicators")
            macro = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM tw_stock_prices")
            tw = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM us_stock_prices")
            us = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM financial_news")
            news = cur.fetchone()[0]
            
            current_counts = {'gold': gold, 'rate': rate, 'macro': macro, 'tw': tw, 'us': us, 'news': news}
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # 格式化輸出
            diffs = {}
            for k, v in current_counts.items():
                diff = v - last_counts[k]
                diffs[k] = f"+{diff}" if diff > 0 and last_counts[k] > 0 else ""
            
            print(f"{timestamp:<10} | {gold:<8} {diffs['gold']:<3} | {rate:<8} {diffs['rate']:<3} | {macro:<8} {diffs['macro']:<3} | {tw:<8} {diffs['tw']:<3} | {us:<8} {diffs['us']:<3} | {news:<8} {diffs['news']:<3}")
            
            last_counts = current_counts
            time.sleep(5)
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 監控失敗: {e}")
        print("請確認資料庫已啟動且密碼正確")

if __name__ == '__main__':
    monitor()
