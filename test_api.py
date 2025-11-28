"""
API伺服器v2.0 自動化測試腳本

測試所有19個API端點並生成詳細報告
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# 配置
BASE_URL = "http://localhost:5000"
TIMEOUT = 10  # 請求超時時間（秒）

# 顏色輸出（Windows支援）
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ''


class APITester:
    """API測試器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        expected_status: int = 200,
        description: str = ""
    ) -> Tuple[bool, str, Dict]:
        """
        測試單個端點
        
        Returns:
            (是否通過, 說明訊息, 回應數據)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=TIMEOUT)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=TIMEOUT)
            else:
                return False, f"不支援的HTTP方法: {method}", {}
            
            # 檢查狀態碼
            if response.status_code != expected_status:
                return False, f"狀態碼錯誤: 期望{expected_status}, 實際{response.status_code}", {}
            
            # 解析JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                return False, "回應不是有效的JSON格式", {}
            
            # 檢查回應時間
            response_time = response.elapsed.total_seconds()
            if response_time > 1.0:
                return True, f"⚠️ 回應時間較慢: {response_time:.2f}秒", response_data
            
            return True, f"✅ 成功 ({response_time*1000:.0f}ms)", response_data
            
        except requests.exceptions.Timeout:
            return False, f"請求超時（>{TIMEOUT}秒）", {}
        except requests.exceptions.ConnectionError:
            return False, "無法連接到API伺服器", {}
        except Exception as e:
            return False, f"錯誤: {str(e)}", {}
    
    def run_test(self, test_name: str, method: str, endpoint: str, **kwargs):
        """執行測試並記錄結果"""
        print(f"\n{'='*60}")
        print(f"📝 測試: {test_name}")
        print(f"   {method} {endpoint}")
        
        passed, message, data = self.test_endpoint(method, endpoint, **kwargs)
        
        # 記錄結果
        result = {
            'test_name': test_name,
            'method': method,
            'endpoint': endpoint,
            'passed': passed,
            'message': message,
            'response_data': data
        }
        self.results.append(result)
        
        if passed:
            if '⚠️' in message:
                self.warnings += 1
                print(f"{YELLOW}{message}{RESET}")
            else:
                self.passed += 1
                print(f"{GREEN}{message}{RESET}")
        else:
            self.failed += 1
            print(f"{RED}❌ 失敗: {message}{RESET}")
        
        # 顯示部分回應數據
        if data and passed:
            self._print_response_preview(data)
    
    def _print_response_preview(self, data: Dict, max_lines: int = 3):
        """顯示回應數據預覽"""
        print(f"{BLUE}回應預覽:{RESET}")
        data_str = json.dumps(data, indent=2, ensure_ascii=False)
        lines = data_str.split('\n')
        
        for i, line in enumerate(lines[:max_lines]):
            print(f"   {line}")
        
        if len(lines) > max_lines:
            print(f"   ... (還有 {len(lines) - max_lines} 行)")
    
    def generate_report(self) -> str:
        """生成測試報告"""
        total = len(self.results)
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        report = f"""
{'='*60}
📊 API測試報告
{'='*60}

測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
API伺服器: {self.base_url}

總測試數: {total}
✅ 通過: {self.passed}
❌ 失敗: {self.failed}
⚠️  警告: {self.warnings}

通過率: {pass_rate:.1f}%

{'='*60}
詳細結果:
{'='*60}

"""
        
        for i, result in enumerate(self.results, 1):
            status = '✅ PASS' if result['passed'] else '❌ FAIL'
            report += f"\n{i}. {result['test_name']}\n"
            report += f"   {result['method']} {result['endpoint']}\n"
            report += f"   狀態: {status}\n"
            report += f"   訊息: {result['message']}\n"
        
        report += f"\n{'='*60}\n"
        
        if self.failed == 0:
            report += f"{GREEN}🎉 所有測試通過！{RESET}\n"
        else:
            report += f"{RED}⚠️ 有 {self.failed} 個測試失敗{RESET}\n"
        
        report += f"{'='*60}\n"
        
        return report


def main():
    """主測試流程"""
    print(f"""
{'='*60}
🚀 API伺服器v2.0 自動化測試
{'='*60}

開始測試所有19個API端點...
""")
    
    tester = APITester()
    
    # ============ 1. 健康檢查 ============
    print(f"\n{BLUE}【分類1：健康檢查】{RESET}")
    
    tester.run_test(
        "健康檢查",
        "GET",
        "/api/health"
    )
    
    # ============ 2. API配置管理 ============
    print(f"\n{BLUE}【分類2：API配置管理】{RESET}")
    
    tester.run_test(
        "查詢API金鑰狀態",
        "GET",
        "/api/config/api-keys"
    )
    
    tester.run_test(
        "同步API金鑰（測試）",
        "POST",
        "/api/config/sync-api-keys",
        data={
            "gemini": "TEST_GEMINI_KEY_AUTO_TEST",
            "alphaVantage": "TEST_ALPHA_KEY_AUTO_TEST"
        }
    )
    
    # ============ 3. 資料庫查詢 ============
    print(f"\n{BLUE}【分類3：資料庫查詢】{RESET}")
    
    tester.run_test(
        "列出所有資料表",
        "GET",
        "/api/database/tables"
    )
    
    tester.run_test(
        "查詢tw_stock_info表格",
        "GET",
        "/api/database/table/tw_stock_info",
        params={"limit": 5}
    )
    
    # ============ 4. 股票資訊 ============
    print(f"\n{BLUE}【分類4：股票資訊】{RESET}")
    
    tester.run_test(
        "獲取台股清單",
        "GET",
        "/api/stocks/list",
        params={"market": "tw", "limit": 10}
    )
    
    tester.run_test(
        "搜尋台積電",
        "GET",
        "/api/stocks/search",
        params={"q": "2330", "market": "tw"}
    )
    
    tester.run_test(
        "獲取台積電詳情",
        "GET",
        "/api/stocks/2330",
        params={"market": "tw"}
    )
    
    # ============ 5. 價格資料 ============
    print(f"\n{BLUE}【分類5：價格資料】{RESET}")
    
    tester.run_test(
        "獲取台積電歷史價格",
        "GET",
        "/api/prices/2330",
        params={"market": "tw", "days": 30}
    )
    
    tester.run_test(
        "獲取台積電最新價格",
        "GET",
        "/api/prices/2330/latest",
        params={"market": "tw"}
    )
    
    # ============ 6. 因子分數 ============
    print(f"\n{BLUE}【分類6：因子分數】{RESET}")
    
    tester.run_test(
        "獲取因子分數",
        "GET",
        "/api/factors/2330",
        params={"market": "tw"},
        expected_status=404  # 可能還沒有數據
    )
    
    tester.run_test(
        "獲取因子歷史",
        "GET",
        "/api/factors/2330/history",
        params={"market": "tw", "days": 90},
        expected_status=200
    )
    
    # ============ 7. TDCC數據 ============
    print(f"\n{BLUE}【分類7：TDCC股權數據】{RESET}")
    
    tester.run_test(
        "獲取TDCC股權分散表",
        "GET",
        "/api/tdcc/2330",
        expected_status=404  # 可能還沒有數據
    )
    
    # ============ 8. 技術指標 ============
    print(f"\n{BLUE}【分類8：技術指標】{RESET}")
    
    tester.run_test(
        "獲取技術指標",
        "GET",
        "/api/indicators/2330",
        params={"market": "tw", "days": 30},
        expected_status=404  # 可能還沒有數據
    )
    
    # ============ 9. AI報告 ============
    print(f"\n{BLUE}【分類9：AI報告】{RESET}")
    
    tester.run_test(
        "獲取AI報告列表",
        "GET",
        "/api/ai/reports",
        params={"type": "daily", "limit": 10}
    )
    
    tester.run_test(
        "獲取AI報告詳情",
        "GET",
        "/api/ai/report/test-report-id",
        expected_status=404  # 測試ID不存在
    )
    
    # ============ 10. 投資組合 ============
    print(f"\n{BLUE}【分類10：投資組合】{RESET}")
    
    tester.run_test(
        "獲取投資組合列表",
        "GET",
        "/api/portfolio/list",
        params={"user_id": 1}
    )
    
    tester.run_test(
        "獲取投資組合持倉",
        "GET",
        "/api/portfolio/1/holdings"
    )
    
    # ============ 生成報告 ============
    report = tester.generate_report()
    print(report)
    
    # 保存報告到文件
    report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        # 移除顏色代碼
        clean_report = report.replace(GREEN, '').replace(RED, '').replace(YELLOW, '').replace(BLUE, '').replace(RESET, '')
        f.write(clean_report)
    
    print(f"\n📄 測試報告已保存至: {report_file}")
    
    # 返回退出碼
    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️ 測試被用戶中斷{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}❌ 測試腳本錯誤: {str(e)}{RESET}")
        sys.exit(1)
