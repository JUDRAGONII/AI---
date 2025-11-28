"""
自動化測試 - 驗證所有核心功能
"""
import requests
import json
from datetime import datetime

BASE = 'http://localhost:5000/api'

print("=" * 80)
print(f"🧪 完整功能測試 - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 80)

tests = {
    '基礎功能': [
        ('健康檢查', f'{BASE}/health'),
        ('台股列表', f'{BASE}/stocks/list?market=tw&limit=5'),
        ('美股列表', f'{BASE}/stocks/list?market=us&limit=5'),
    ],
    '數據查詢': [
        ('台積電詳情', f'{BASE}/stocks/2330?market=tw'),
        ('台積電價格', f'{BASE}/prices/2330?market=tw&days=7'),
        ('蘋果詳情', f'{BASE}/stocks/AAPL?market=us'),
    ],
    '系統功能': [
        ('資料表列表', f'{BASE}/database/tables'),
        ('API金鑰', f'{BASE}/config/api-keys'),
    ],
}

total = 0
passed = 0

for category, test_list in tests.items():
    print(f"\n【{category}】")
    for name, url in test_list:
        try:
            resp = requests.get(url, timeout=3)
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"  {status} {name}: {resp.status_code}")
            if resp.status_code == 200:
                passed += 1
            total += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:30]}")
            total += 1

print("\n" + "=" * 80)
print(f"📊 結果: {passed}/{total} 通過 ({passed/total*100:.0f}%)")
print("=" * 80)
