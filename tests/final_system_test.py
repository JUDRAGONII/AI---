"""
系統全面功能測試修正版 - 正確API路徑
"""

import requests
import sys
from datetime import datetime

API_BASE = 'http://localhost:5000/api'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

class SystemTester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []
        
    def run_all_tests(self):
        """執行所有測試"""
        print("\n" + "="*60)
        print(f"AI投資分析儀系統測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 測試1: 系統健康
        try:
            response = requests.get(f'{API_BASE}/health', timeout=5)
            if response.status_code == 200:
                print_success(f"系統健康檢查OK")
                self.passed_tests += 1
            else:
                self.failed_tests.append("健康檢查")
            self.total_tests += 1
        except Exception as e:
            print_error(f"健康檢查失敗: {e}")
            self.failed_tests.append("健康檢查")
            self.total_tests += 1
        
        # 測試2: 台股列表
        try:
            response = requests.get(f'{API_BASE}/stocks/list?market=tw&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"台股列表: {len(data['stocks'])} 支")
                self.passed_tests += 1
            else:
                self.failed_tests.append("台股列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"台股列表失敗: {e}")
            self.failed_tests.append("台股列表")
            self.total_tests += 1
        
        # 測試3: 美股列表
        try:
            response = requests.get(f'{API_BASE}/stocks/list?market=us&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"美股列表: {len(data['stocks'])} 支")
                self.passed_tests += 1
            else:
                self.failed_tests.append("美股列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"美股列表失敗: {e}")
            self.failed_tests.append("美股列表")
            self.total_tests += 1
        
        # 測試4: 台積電詳情
        try:
            response = requests.get(f'{API_BASE}/stocks/2330?market=tw', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"台積電詳情: {data.get('stock_name', 'N/A')}")
                self.passed_tests += 1
            else:
                self.failed_tests.append("個股詳情")
            self.total_tests += 1
        except Exception as e:
            print_error(f"個股詳情失敗: {e}")
            self.failed_tests.append("個股詳情")
            self.total_tests += 1
        
        # 測試5: 價格歷史（修正：返回'data'）
        try:
            response = requests.get(f'{API_BASE}/prices/2330?market=tw&days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"價格歷史: {len(data['data'])} 筆")
                self.passed_tests += 1
            else:
                self.failed_tests.append("價格歷史")
            self.total_tests += 1
        except Exception as e:
            print_error(f"價格歷史失敗: {e}")
            self.failed_tests.append("價格歷史")
            self.total_tests += 1
        
        # 測試6-9: 技術指標（修正：路徑為/indicators/<code>/ma）
        indicators = [('ma', 'MA'), ('rsi', 'RSI'), ('macd', 'MACD'), ('bollinger', '布林通道')]
        for endpoint, name in indicators:
            try:
                response = requests.get(f'{API_BASE}/indicators/2330/{endpoint}?market=tw', timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"{name}: {len(data.get('data', []))} 筆")
                    self.passed_tests += 1
                else:
                    print_error(f"{name}失敗: {response.status_code}")
                    self.failed_tests.append(name)
                self.total_tests += 1
            except Exception as e:
                print_error(f"{name}錯誤: {e}")
                self.failed_tests.append(name)
                self.total_tests += 1
        
        # 測試10: 黃金價格
        try:
            response = requests.get(f'{API_BASE}/commodity/GOLD?days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"黃金價格: {data['count']} 筆")
                self.passed_tests += 1
            else:
                self.failed_tests.append("黃金價格")
            self.total_tests += 1
        except Exception as e:
            print_error(f"黃金價格失敗: {e}")
            self.failed_tests.append("黃金價格")
            self.total_tests += 1
        
        # 測試11: USD/TWD匯率
        try:
            response = requests.get(f'{API_BASE}/forex/USDTWD?days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"USD/TWD匯率: {data['count']} 筆")
                self.passed_tests += 1
            else:
                self.failed_tests.append("USD/TWD匯率")
            self.total_tests += 1
        except Exception as e:
            print_error(f"USD/TWD匯率失敗: {e}")
            self.failed_tests.append("USD/TWD匯率")
            self.total_tests += 1
        
        # 測試12: 市場總覽
        try:
            response = requests.get(f'{API_BASE}/market/summary', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"市場總覽OK")
                print_info(f"  台股: {data['stocks']['tw']} 支, 價格: {data['stocks']['tw_prices']} 筆")
                print_info(f"  美股: {data['stocks']['us']} 支, 價格: {data['stocks']['us_prices']} 筆")
                print_info(f"  黃金: {data['gold']['count']} 筆, 匯率: {data['forex']['count']} 筆")
                self.passed_tests += 1
            else:
                self.failed_tests.append("市場總覽")
            self.total_tests += 1
        except Exception as e:
            print_error(f"市場總覽失敗: {e}")
            self.failed_tests.append("市場總覽")
            self.total_tests += 1
        
        # 測試13: AI測試連接
        try:
            response = requests.get(f'{API_BASE}/ai/test-connection', timeout=15)
            if response.status_code == 200:
                data = response.json()
                print_success(f"AI連接: {data.get('message', 'OK')}")
                self.passed_tests += 1
            else:
                data = response.json()
                print_warning(f"AI連接: {data.get('error', '未配置')}")
                print_info("  需要設置config/.env中的GOOGLE_AI_API_KEY")
                self.failed_tests.append("AI連接")
            self.total_tests += 1
        except Exception as e:
            print_warning(f"AI連接: 未配置")
            self.failed_tests.append("AI連接")
            self.total_tests += 1
        
        # 測試14: AI報告列表
        try:
            response = requests.get(f'{API_BASE}/ai/reports?type=market&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('reports', []))
                if count > 0:
                    print_success(f"AI報告列表: {count} 份")
                else:
                    print_info(f"AI報告列表: 0 份（尚未生成報告）")
                self.passed_tests += 1
            else:
                self.failed_tests.append("AI報告列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"AI報告列表失敗: {e}")
            self.failed_tests.append("AI報告列表")
            self.total_tests += 1
        
        # 總結
        print("\n" + "="*60)
        print("測試結果總結")
        print("="*60)
        print(f"總測試數: {self.total_tests}")
        print_success(f"通過: {self.passed_tests}")
        if self.failed_tests:
            print_warning(f"注意: {len(self.failed_tests)} 項")
            for test in self.failed_tests:
                print_info(f"  - {test}")
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n通過率: {pass_rate:.1f}%")
        
        if pass_rate >= 85:
            print_success("系統狀態: 優秀 ✨")
        elif pass_rate >= 70:
            print_info("系統狀態: 良好 👍")
        else:
            print_warning("系統狀態: 需要改進")
        
        print("="*60)
        
        return pass_rate

if __name__ == "__main__":
    tester = SystemTester()
    pass_rate = tester.run_all_tests()
    
    sys.exit(0 if pass_rate >= 70 else 1)
