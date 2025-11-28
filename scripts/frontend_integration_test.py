"""
階段5：前端API整合測試腳本
測試所有API端點並生成整合報告
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

tests = [
    ('健康檢查', 'GET', '/health'),
    ('股票列表', 'GET', '/stocks/list?market=tw&limit=10'),
    ('台積電資訊', 'GET', '/stocks/2330?market=tw'),
    ('台積電價格', 'GET', '/prices/2330?market=tw&days=7'),
    ('系統配置', 'GET', '/config/api-keys'),
    ('資料表列表', 'GET', '/database/tables'),
]

results = []

print("=" * 80)
print(f"🧪 前端整合測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for name, method, endpoint in tests:
    try:
        url = BASE_URL + endpoint
        resp = requests.get(url, timeout=5)
        
        status = "✅" if resp.status_code == 200 else "❌"
        print(f"{status} {name}: {resp.status_code}")
        
        results.append({
            'test': name,
            'status': resp.status_code,
            'success': resp.status_code == 200
        })
        
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        results.append({'test': name, 'status': 'ERROR', 'success': False})

# 統計
total = len(results)
passed = sum(1 for r in results if r['success'])

print("\n" + "=" * 80)
print(f"📊 測試結果: {passed}/{total} 通過 ({passed/total*100:.0f}%)")
print("=" * 80)

if passed == total:
    print("🎉 所有測試通過！前端可以開始整合")
else:
    print(f"⚠️  有 {total-passed} 個測試失敗")
