"""
系統完整性測試腳本
測試所有API端點、數據庫連接、AI功能
"""

import requests
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

API_BASE = 'http://localhost:5000/api'
test_results = []


def test_api(name, method, endpoint, expected_status=200, data=None):
    """測試API端點"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        success = response.status_code == expected_status
        test_results.append({
            'name': name,
            'success': success,
            'status': response.status_code,
            'message': 'OK' if success else f'Expected {expected_status}, got {response.status_code}'
        })
        return success
    except Exception as e:
        test_results.append({
            'name': name,
            'success': False,
            'status': 'ERROR',
            'message': str(e)
        })
        return False


def test_database():
    """測試資料庫連接"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '15432')),
            database=os.getenv('DB_NAME', 'quant_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        cursor = conn.cursor()
        
        # 測試查詢
        cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
        tw_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM us_stock_info")
        us_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        test_results.append({
            'name': '資料庫連接',
            'success': True,
            'status': 'OK',
            'message': f'台股{tw_count}支, 美股{us_count}支'
        })
        return True
    except Exception as e:
        test_results.append({
            'name': '資料庫連接',
            'success': False,
            'status': 'ERROR',
            'message': str(e)
        })
        return False


def run_all_tests():
    """執行所有測試"""
    print("=" * 60)
    print("🧪 系統完整性測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 資料庫測試
    print("📊 資料庫測試...")
    test_database()
    
    # API端點測試
    print("\n🔌 API端點測試...")
    
    # 基礎端點
    test_api('健康檢查', 'GET', '/health')
    test_api('股票列表-台股', 'GET', '/stocks/list?market=tw&limit=10')
    test_api('股票列表-美股', 'GET', '/stocks/list?market=us&limit=10')
    test_api('股票詳情', 'GET', '/stocks/2330?market=tw')
    test_api('價格歷史', 'GET', '/prices/2330?market=tw&days=30')
    
    # 技術指標端點
    test_api('MA指標', 'GET', '/indicators/2330/ma?market=tw&period=20')
    test_api('RSI指標', 'GET', '/indicators/2330/rsi?market=tw')
    test_api('MACD指標', 'GET', '/indicators/2330/macd?market=tw')
    test_api('布林通道', 'GET', '/indicators/2330/bollinger?market=tw')
    
    # 市場數據端點
    test_api('黃金價格', 'GET', '/commodity/GOLD?days=30')
    test_api('匯率數據', 'GET', '/forex/USDTWD?days=30')
    test_api('市場總覽', 'GET', '/market/summary')
    
    # 資料庫管理
    test_api('資料表列表', 'GET', '/database/tables')
    
    # AI端點測試（可能失敗，取決於API金鑰配置）
    print("\n🤖 AI功能測試...")
    test_api('AI連接測試', 'GET', '/ai/test-connection')
    
    # 列印測試結果
    print("\n" + "=" * 60)
    print("📋 測試結果摘要")
    print("=" * 60)
    
    success_count = sum(1 for r in test_results if r['success'])
    total_count = len(test_results)
    
    for result in test_results:
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {result['name']}: {result['message']}")
    
    print("\n" + "=" * 60)
    print(f"通過: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print("=" * 60)
    
    # 生成測試報告
    report_file = 'test_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"系統測試報告\n")
        f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"測試結果: {success_count}/{total_count} 通過\n\n")
        
        for result in test_results:
            f.write(f"{'[PASS]' if result['success'] else '[FAIL]'} {result['name']}: {result['message']}\n")
    
    print(f"\n📄 測試報告已儲存: {report_file}")
    
    return success_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
