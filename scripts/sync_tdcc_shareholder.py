"""
TDCC大戶持股數據同步腳本
從TDCC OpenAPI獲取股權分散表數據並存入資料庫
"""

import requests
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))


def get_db():
    """獲取資料庫連接"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )


def fetch_tdcc_data(stock_code: str, date: str = None):
    """
    從TDCC OpenAPI獲取股權分散表數據
    
    Args:
        stock_code: 股票代碼 (4碼)
        date: 查詢日期 (YYYYMMDD)，預設為最近一個交易日
        
    Returns:
        dict: 股權分散數據
    """
    # TDCC OpenAPI endpoint
    # 注意：這是示範URL，實際需要根據TDCC官方文檔調整
    base_url = "https://openapi.tdcc.com.tw/v1/shareholding"
    
    if not date:
        # 預設查詢最近交易日
        date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    params = {
        'stock_code': stock_code,
        'date': date
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 獲取TDCC數據失敗 ({stock_code}): {e}")
        return None


def save_tdcc_data(stock_code: str, data: dict):
    """
    儲存TDCC數據到資料庫
    
    Args:
        stock_code: 股票代碼
        data: TDCC數據
    """
    if not data or 'data' not in data:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 準備插入數據
        query = """
            INSERT INTO tdcc_shareholder_distribution 
            (stock_code, data_date, level_name, holder_count, shares, percentage, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_code, data_date, level_name) 
            DO UPDATE SET 
                holder_count = EXCLUDED.holder_count,
                shares = EXCLUDED.shares,
                percentage = EXCLUDED.percentage,
                updated_at = NOW()
        """
        
        # 假設data結構：[{level, holders, shares, percentage}, ...]
        records = []
        data_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        for item in data.get('data', []):
            records.append((
                stock_code,
                data_date,
                item.get('level'),
                item.get('holders', 0),
                int(item.get('shares', 0)),
                float(item.get('percentage', 0)),
                datetime.now()
            ))
        
        # 批次插入
        cursor.executemany(query, records)
        conn.commit()
        
        print(f"✅ {stock_code} TDCC數據已儲存 ({len(records)} 筆)")
        return True
        
    except Exception as e:
        print(f"❌ 儲存數據失敗 ({stock_code}): {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def sync_tdcc_for_all_stocks():
    """同步所有台股的TDCC數據"""
    print("=" * 60)
    print("🚀 TDCC大戶持股數據同步")
    print("=" * 60)
    
    # 獲取所有台股代碼
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_code FROM tw_stock_info ORDER BY stock_code")
    stock_codes = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    print(f"📊 找到 {len(stock_codes)} 支台股")
    
    success_count = 0
    fail_count = 0
    
    for idx, stock_code in enumerate(stock_codes, 1):
        print(f"\n[{idx}/{len(stock_codes)}] 處理 {stock_code}...")
        
        # 獲取TDCC數據
        data = fetch_tdcc_data(stock_code)
        
        if data:
            # 儲存數據
            if save_tdcc_data(stock_code, data):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        # API速率限制（避免被封鎖）
        if idx % 10 == 0:
            print("⏸️  暫停3秒避免API速率限制...")
            time.sleep(3)
        else:
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"✅ 同步完成！成功: {success_count}, 失敗: {fail_count}")
    print("=" * 60)


def calculate_institutional_ratio(stock_code: str):
    """
    計算大戶同步率
    
    Args:
        stock_code: 股票代碼
        
    Returns:
        dict: 大戶同步率數據
    """
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    try:
        # 查詢最新的股權分散數據
        cursor.execute("""
            SELECT level_name, holder_count, shares, percentage
            FROM tdcc_shareholder_distribution
            WHERE stock_code = %s
            ORDER BY data_date DESC, id
            LIMIT 100
        """, (stock_code,))
        
        data = cursor.fetchall()
        
        if not data:
            return None
        
        # 計算大戶持股（假設1000張以上為大戶）
        institutional_shares = sum(int(row['shares']) for row in data if '1000' in row['level_name'])
        total_shares = sum(int(row['shares']) for row in data)
        
        ratio = (institutional_shares / total_shares * 100) if total_shares > 0 else 0
        
        return {
            'stock_code': stock_code,
            'institutional_shares': institutional_shares,
            'total_shares': total_shares,
            'institutional_ratio': round(ratio, 2),
            'data_count': len(data)
        }
        
    except Exception as e:
        print(f"❌ 計算大戶同步率失敗 ({stock_code}): {e}")
        return None
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    import sys
    
    print("\n🔧 TDCC大戶持股數據同步工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'sync':
            # 同步所有股票
            sync_tdcc_for_all_stocks()
        elif command == 'test':
            # 測試單一股票
            test_code = sys.argv[2] if len(sys.argv) > 2 else '2330'
            print(f"測試股票: {test_code}\n")
            data = fetch_tdcc_data(test_code)
            if data:
                print(f"✅ 成功獲取數據")
                print(f"數據: {data}")
                save_tdcc_data(test_code, data)
            else:
                print(f"❌ 獲取失敗")
        elif command == 'ratio':
            # 計算大戶同步率
            stock_code = sys.argv[2] if len(sys.argv) > 2 else '2330'
            result = calculate_institutional_ratio(stock_code)
            if result:
                print(f"\n📊 {stock_code} 大戶持股分析")
                print(f"   大戶持股: {result['institutional_shares']:,} 張")
                print(f"   總持股: {result['total_shares']:,} 張")
                print(f"   大戶同步率: {result['institutional_ratio']}%")
            else:
                print(f"❌ 無數據")
        else:
            print(f"未知命令: {command}")
            print("可用命令: sync, test, ratio")
    else:
        print("用法:")
        print("  python sync_tdcc_shareholder.py sync        # 同步所有股票")
        print("  python sync_tdcc_shareholder.py test 2330   # 測試單一股票")
        print("  python sync_tdcc_shareholder.py ratio 2330  # 計算大戶同步率")
    
    print("=" * 60)
