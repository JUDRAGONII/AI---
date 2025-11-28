"""
最終系統驗證測試
測試所有核心功能並生成完整報告
"""
import requests
import json
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

BASE = 'http://localhost:5000/api'

print("=" * 100)
print(f"{Fore.CYAN}🎯 系統完整驗證測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
print("=" * 100)

test_suites = {
    '基礎功能': [
        ('健康檢查', f'{BASE}/health', '應返回healthy狀態'),
        ('資料表列表', f'{BASE}/database/tables', '應返回所有資料表'),
    ],
    '台股功能': [
        ('台股列表', f'{BASE}/stocks/list?market=tw&limit=10', '應返回10支台股'),
        ('台積電詳情', f'{BASE}/stocks/2330?market=tw', '應返回台積電資訊'),
        ('台積電價格', f'{BASE}/prices/2330?market=tw&days=7', '應返回近7天價格'),
    ],
    '美股功能': [
        ('美股列表', f'{BASE}/stocks/list?market=us&limit=10', '應返回美股列表'),
        ('蘋果詳情', f'{BASE}/stocks/AAPL?market=us', '應返回蘋果資訊'),
    ],
    '系統管理': [
        ('API金鑰', f'{BASE}/config/api-keys', '應返回金鑰狀態'),
    ],
}

results = []
total = 0
passed = 0

for suite_name, tests in test_suites.items():
    print(f"\n{Fore.YELLOW}【{suite_name}】{Style.RESET_ALL}")
    
    for name, url, expected in tests:
        total += 1
        try:
            resp = requests.get(url, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                status = f"{Fore.GREEN}✅{Style.RESET_ALL}"
                passed += 1
                detail = "成功"
                
                # 額外驗證
                if 'count' in data and data['count'] > 0:
                    detail = f"成功 ({data['count']}筆)"
                elif 'status' in data:
                    detail = f"成功 (狀態:{data['status']})"
                    
            else:
                status = f"{Fore.RED}❌{Style.RESET_ALL}"
                detail = f"HTTP {resp.status_code}"
                
            print(f"  {status} {name}: {detail}")
            print(f"     {Fore.CYAN}→ {expected}{Style.RESET_ALL}")
            
            results.append({
                'suite': suite_name,
                'test': name,
                'status': resp.status_code,
                'success': resp.status_code == 200,
                'detail': detail
            })
            
        except requests.exceptions.Timeout:
            print(f"  {Fore.RED}❌{Style.RESET_ALL} {name}: 請求超時")
            results.append({'suite': suite_name, 'test': name, 'status': 'TIMEOUT', 'success': False})
        except Exception as e:
            print(f"  {Fore.RED}❌{Style.RESET_ALL} {name}: {str(e)[:40]}")
            results.append({'suite': suite_name, 'test': name, 'status': 'ERROR', 'success': False})

# 統計結果
print("\n" + "=" * 100)
pass_rate = (passed / total * 100) if total > 0 else 0

if pass_rate >= 90:
    color = Fore.GREEN
    grade = "優秀"
elif pass_rate >= 75:
    color = Fore.YELLOW
    grade = "良好"
else:
    color = Fore.RED
    grade = "需改進"

print(f"{color}📊 測試結果: {passed}/{total} 通過 ({pass_rate:.1f}%) - {grade}{Style.RESET_ALL}")
print("=" * 100)

# 詳細報告
print(f"\n{Fore.CYAN}📋 詳細統計{Style.RESET_ALL}")
for suite_name in test_suites.keys():
    suite_results = [r for r in results if r['suite'] == suite_name]
    suite_passed = sum(1 for r in suite_results if r['success'])
    suite_total = len(suite_results)
    suite_rate = (suite_passed / suite_total * 100) if suite_total > 0 else 0
    
    print(f"  {suite_name}: {suite_passed}/{suite_total} ({suite_rate:.0f}%)")

# 建議
print(f"\n{Fore.CYAN}💡 建議{Style.RESET_ALL}")
if pass_rate >= 90:
    print("  ✅ 系統運行良好，可以進入生產環境")
elif pass_rate >= 75:
    print("  ⚠️  部分功能需要修復，建議優化後再上線")
else:
    print("  ❌ 系統存在嚴重問題，請優先修復失敗項目")

print("\n" + "=" * 100)
