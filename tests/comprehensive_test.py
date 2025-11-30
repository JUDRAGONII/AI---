"""
系統全面功能測試 - 覆蓋V9.3規格書所有功能
測試內容：
1. 資料庫連接與數據完整性
2. 所有API端點
3. 技術指標計算
4. 量化因子計算
5. AI功能
6. TDCC大戶持股
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
        
    def test_health(self):
        """測試系統健康狀態"""
        print("\n" + "="*60)
        print("1. 系統健康檢查")
        print("="*60)
        
        try:
            response = requests.get(f'{API_BASE}/health', timeout=5)
            if response.status_code == 200:
                print_success(f"API服務正常運行: {response.json()}")
                self.passed_tests += 1
            else:
                print_error(f"API服務異常: {response.status_code}")
                self.failed_tests.append("Health Check")
            self.total_tests += 1
        except Exception as e:
            print_error(f"無法連接API服務: {e}")
            self.failed_tests.append("Health Check")
            self.total_tests += 1
    
    def test_database(self):
        """測試資料庫連接與數據"""
        print("\n" + "="*60)
        print("2. 資料庫測試")
        print("="*60)
        
        # 測試台股列表
        try:
            response = requests.get(f'{API_BASE}/stocks/list?market=tw&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"台股列表: 獲取到 {len(data['stocks'])} 支股票")
                self.passed_tests += 1
            else:
                print_error(f"台股列表失敗: {response.status_code}")
                self.failed_tests.append("台股列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"台股列表錯誤: {e}")
            self.failed_tests.append("台股列表")
            self.total_tests += 1
        
        # 測試美股列表
        try:
            response = requests.get(f'{API_BASE}/stocks/list?market=us&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"美股列表: 獲取到 {len(data['stocks'])} 支股票")
                self.passed_tests += 1
            else:
                print_error(f"美股列表失敗: {response.status_code}")
                self.failed_tests.append("美股列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"美股列表錯誤: {e}")
            self.failed_tests.append("美股列表")
            self.total_tests += 1
    
    def test_stock_details(self):
        """測試個股詳情"""
        print("\n" + "="*60)
        print("3. 個股詳情測試")
        print("="*60)
        
        # 台股
        try:
            response = requests.get(f'{API_BASE}/stocks/2330?market=tw', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"台積電(2330): {data.get('stock_name', 'N/A')}")
                self.passed_tests += 1
            else:
                print_error(f"台積電詳情失敗: {response.status_code}")
                self.failed_tests.append("台積電詳情")
            self.total_tests += 1
        except Exception as e:
            print_error(f"台積電詳情錯誤: {e}")
            self.failed_tests.append("台積電詳情")
            self.total_tests += 1
        
        # 美股
        try:
            response = requests.get(f'{API_BASE}/stocks/AAPL?market=us', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Apple(AAPL): {data.get('stock_name', 'N/A')}")
                self.passed_tests += 1
            else:
                print_error(f"Apple詳情失敗: {response.status_code}")
                self.failed_tests.append("Apple詳情")
            self.total_tests += 1
        except Exception as e:
            print_error(f"Apple詳情錯誤: {e}")
            self.failed_tests.append("Apple詳情")
            self.total_tests += 1
    
    def test_prices(self):
        """測試價格歷史"""
        print("\n" + "="*60)
        print("4. 價格歷史測試")
        print("="*60)
        
        try:
            response = requests.get(f'{API_BASE}/prices/2330?market=tw&days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"2330價格歷史: {len(data['prices'])} 筆")
                self.passed_tests += 1
            else:
                print_error(f"價格歷史失敗: {response.status_code}")
                self.failed_tests.append("價格歷史")
            self.total_tests += 1
        except Exception as e:
            print_error(f"價格歷史錯誤: {e}")
            self.failed_tests.append("價格歷史")
            self.total_tests += 1
    
    def test_technical_indicators(self):
        """測試技術指標"""
        print("\n" + "="*60)
        print("5. 技術指標測試")
        print("="*60)
        
        indicators = ['ma', 'rsi', 'macd', 'bollinger']
        for indicator in indicators:
            try:
                response = requests.get(f'{API_BASE}/indicators/{indicator}/2330?market=tw&days=60', timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"{indicator.upper()}: {len(data.get('data', []))} 筆")
                    self.passed_tests += 1
                else:
                    print_error(f"{indicator.upper()}失敗: {response.status_code}")
                    self.failed_tests.append(f"{indicator.upper()}")
                self.total_tests += 1
            except Exception as e:
                print_error(f"{indicator.upper()}錯誤: {e}")
                self.failed_tests.append(f"{indicator.upper()}")
                self.total_tests += 1
    
    def test_factors(self):
        """測試量化因子"""
        print("\n" + "="*60)
        print("6. 量化因子測試")
        print("="*60)
        
        factors = ['value', 'quality', 'momentum', 'size', 'volatility', 'growth']
        for factor in factors:
            try:
                response = requests.get(f'{API_BASE}/factors/{factor}/2330?market=tw', timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"{factor.capitalize()}因子: 分數 {data.get('score', 'N/A')}")
                    self.passed_tests += 1
                else:
                    print_error(f"{factor}因子失敗: {response.status_code}")
                    self.failed_tests.append(f"{factor}因子")
                self.total_tests += 1
            except Exception as e:
                print_error(f"{factor}因子錯誤: {e}")
                self.failed_tests.append(f"{factor}因子")
                self.total_tests += 1
    
    def test_commodity_forex(self):
        """測試商品與匯率"""
        print("\n" + "="*60)
        print("7. 商品與匯率測試")
        print("="*60)
        
        # 黃金
        try:
            response = requests.get(f'{API_BASE}/commodity/GOLD?days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"黃金價格: {data['count']} 筆")
                self.passed_tests += 1
            else:
                print_error(f"黃金價格失敗: {response.status_code}")
                self.failed_tests.append("黃金價格")
            self.total_tests += 1
        except Exception as e:
            print_error(f"黃金價格錯誤: {e}")
            self.failed_tests.append("黃金價格")
            self.total_tests += 1
        
        # 匯率
        try:
            response = requests.get(f'{API_BASE}/forex/USDTWD?days=30', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"USD/TWD匯率: {data['count']} 筆")
                self.passed_tests += 1
            else:
                print_error(f"USD/TWD匯率失敗: {response.status_code}")
                self.failed_tests.append("USD/TWD匯率")
            self.total_tests += 1
        except Exception as e:
            print_error(f"USD/TWD匯率錯誤: {e}")
            self.failed_tests.append("USD/TWD匯率")
            self.total_tests += 1
    
    def test_market_summary(self):
        """測試市場總覽"""
        print("\n" + "="*60)
        print("8. 市場總覽測試")
        print("="*60)
        
        try:
            response = requests.get(f'{API_BASE}/market/summary', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"市場總覽OK - 黃金: ${data['gold']['price']}, USD/TWD: {data['forex']['usd_twd']}")
                print_info(f"  台股價格數: {data['stocks']['tw_prices']}")
                print_info(f"  美股價格數: {data['stocks']['us_prices']}")
                print_info(f"  黃金數據: {data['gold']['count']} 筆")
                print_info(f"  匯率數據: {data['forex']['count']} 筆")
                self.passed_tests += 1
            else:
                print_error(f"市場總覽失敗: {response.status_code}")
                self.failed_tests.append("市場總覽")
            self.total_tests += 1
        except Exception as e:
            print_error(f"市場總覽錯誤: {e}")
            self.failed_tests.append("市場總覽")
            self.total_tests += 1
    
    def test_tdcc(self):
        """測試TDCC大戶持股"""
        print("\n" + "="*60)
        print("9. TDCC大戶持股測試")
        print("="*60)
        
        try:
            response = requests.get(f'{API_BASE}/tdcc/2330?limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"2330 TDCC: {len(data.get('data', []))} 筆記錄")
                self.passed_tests += 1
            else:
                print_error(f"TDCC失敗: {response.status_code}")
                self.failed_tests.append("TDCC")
            self.total_tests += 1
        except Exception as e:
            print_error(f"TDCC錯誤: {e}")
            self.failed_tests.append("TDCC")
            self.total_tests += 1
    
    def test_ai_features(self):
        """測試AI功能"""
        print("\n" + "="*60)
        print("10. AI功能測試")
        print("="*60)
        
        # AI連接測試
        try:
            response = requests.get(f'{API_BASE}/ai/test-connection', timeout=15)
            if response.status_code == 200:
                data = response.json()
                print_success(f"AI連接: {data.get('message', 'OK')}")
                self.passed_tests += 1
            else:
                data = response.json()
                print_warning(f"AI連接失敗: {data.get('error', response.status_code)}")
                print_info("  請確認config/.env中的GOOGLE_AI_API_KEY設置")
                self.failed_tests.append("AI連接")
            self.total_tests += 1
        except Exception as e:
            print_error(f"AI連接錯誤: {e}")
            self.failed_tests.append("AI連接")
            self.total_tests += 1
        
        # AI報告列表
        try:
            response = requests.get(f'{API_BASE}/ai/reports?type=market&limit=5', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"AI報告列表: {len(data['reports'])} 份")
                self.passed_tests += 1
            else:
                print_error(f"AI報告列表失敗: {response.status_code}")
                self.failed_tests.append("AI報告列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"AI報告列表錯誤: {e}")
            self.failed_tests.append("AI報告列表")
            self.total_tests += 1
    
    def test_database_tables(self):
        """測試資料表列表"""
        print("\n" + "="*60)
        print("11. 資料表列表測試")
        print("="*60)
        
        try:
            response = requests.get(f'{API_BASE}/tables', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"資料表: {len(data['tables'])} 個")
                for table in data['tables'][:10]:
                    print_info(f"  - {table}")
                self.passed_tests += 1
            else:
                print_error(f"資料表列表失敗: {response.status_code}")
                self.failed_tests.append("資料表列表")
            self.total_tests += 1
        except Exception as e:
            print_error(f"資料表列表錯誤: {e}")
            self.failed_tests.append("資料表列表")
            self.total_tests += 1
    
    def run_all_tests(self):
        """執行所有測試"""
        print("\n" + "="*60)
        print(f"系統全面功能測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.test_health()
        self.test_database()
        self.test_stock_details()
        self.test_prices()
        self.test_technical_indicators()
        self.test_factors()
        self.test_commodity_forex()
        self.test_market_summary()
        self.test_tdcc()
        self.test_ai_features()
        self.test_database_tables()
        
        # 總結
        print("\n" + "="*60)
        print("測試結果總結")
        print("="*60)
        print(f"總測試數: {self.total_tests}")
        print_success(f"通過: {self.passed_tests}")
        if self.failed_tests:
            print_error(f"失敗: {len(self.failed_tests)}")
            print("\n失敗項目:")
            for test in self.failed_tests:
                print_error(f"  - {test}")
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n通過率: {pass_rate:.1f}%")
        print("="*60)
        
        return pass_rate

if __name__ == "__main__":
    tester = SystemTester()
    pass_rate = tester.run_all_tests()
    
    # 根據通過率決定退出碼
    sys.exit(0 if pass_rate >= 90 else 1)
