"""
擴展台股數據 - 從50支擴展到100支
基於市值和交易量選擇優質股票
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# 台股前100支（市值排序）
TW_STOCKS_100 = [
    # 原有50支
    '2330', '2317', '2454', '2308', '2881', '2882', '2891', '2892', '2886', '2884',
    '2412', '2382', '1301', '1303', '1326', '2357', '2303', '3008', '2002', '6505',
    '2887', '2880', '2885', '2890', '1216', '2379', '2377', '2327', '3711', '2345',
    '6415', '6669', '5880', '2912', '2408', '3045', '2301', '2353', '1101', '2395',
    '3231', '5871', '2883', '6505', '1102', '2892', '2609', '2324', '2344', '2371',
    # 新增50支
    '2409', '2603', '1605', '3481', '6176', '2888', '2356', '5483', '1216', '9910',
    '2049', '3037', '6269', '2207', '2618', '2201', '2809', '5871', '2834', '2610',
    '1303', '3034', '1402', '1590', '2809', '4904', '2915', '1314', '2474', '6176',
    '3231', '2841', '3532', '2383', '4938', '2915', '3711', '4958', '5347', '2204',
    '6781', '3552', '2352', '1476', '3481', '5388', '6278', '6409', '2832', '2385'
]

def expand_tw_stocks():
    print("=" * 60)
    print("📈 擴展台股數據：50支 → 100支")
    print("=" * 60)
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = conn.cursor()
    
    # 檢查現有數據
    cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
    existing = cursor.fetchone()[0]
    print(f"現有台股：{existing}支")
    
    stock_count = 0
    
    # 獲取股票列表
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 獲取 {len(data)} 支股票資訊")
            
            # 過濾目標股票
            for item in data:
                code = item.get('Code', '').strip()
                if code in TW_STOCKS_100:
                    try:
                        cursor.execute("""
                            INSERT INTO tw_stock_info 
                            (stock_code, stock_name, market)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (stock_code) DO UPDATE
                            SET stock_name = EXCLUDED.stock_name
                        """, (code, item.get('Name', code), '上市'))
                        stock_count += 1
                    except:
                        continue
            
            conn.commit()
            print(f"✅ 成功寫入/更新 {stock_count} 支股票")
            
            # 驗證
            cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
            total = cursor.fetchone()[0]
            print(f"📊 資料庫總計: {total} 支台股")
            
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    return stock_count

if __name__ == '__main__':
    result = expand_tw_stocks()
    print(f"\n🎉 完成！共處理 {result} 支股票")
