"""
AI功能專項測試腳本
測試所有AI相關端點與功能
"""

import requests
import json
import time
from datetime import datetime

API_BASE = 'http://localhost:5000/api'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

class AIFunctionTester:
    def __init__(self):
        self.results = {
            'connection': False,
            'report_generation': False,
            'report_list': False,
            'report_detail': False
        }
    
    def test_connection(self):
        """測試AI連接"""
        print_header("測試 1: AI 連接測試")
        
        try:
            print_info("發送請求至 /api/ai/test-connection...")
            response = requests.get(f'{API_BASE}/ai/test-connection', timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"AI連接成功！")
                print_info(f"  狀態: {data.get('status')}")
                print_info(f"  訊息: {data.get('message')}")
                print_info(f"  模型: {data.get('model')}")
                if 'response' in data:
                    print_info(f"  AI回應: {data.get('response')}")
                self.results['connection'] = True
                return True
            else:
                data = response.json()
                print_error(f"AI連接失敗: {data.get('error')}")
                print_info("  請檢查 config/.env 中的 GOOGLE_AI_API_KEY 是否正確")
                return False
                
        except Exception as e:
            print_error(f"AI連接測試異常: {e}")
            return False
    
    def test_report_generation(self):
        """測試AI報告生成"""
        print_header("測試 2: AI 報告生成")
        
        try:
            print_info("準備生成市場分析報告...")
            
            market_data = {
                "market_data": {
                    "taiex": 17450,
                    "sp500": 4560,
                    "nasdaq": 14200,
                    "vix": 15.8,
                    "gold": 2040.50,
                    "usdtwd": 31.4
                }
            }
            
            print_info(f"市場數據: 台股{market_data['market_data']['taiex']}, "
                      f"S&P500 {market_data['market_data']['sp500']}, "
                      f"黃金${market_data['market_data']['gold']}")
            
            response = requests.post(
                f'{API_BASE}/ai/market-report',
                json=market_data,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("報告生成成功！")
                print_info(f"  報告ID: {data.get('id')}")
                print_info(f"  情緒: {data.get('sentiment')}")
                print_info(f"  生成時間: {data.get('created_at')}")
                
                # 顯示報告內容的前300字
                report_preview = data.get('report', '')[:300]
                print_info(f"  報告預覽: {report_preview}...")
                
                # 保存完整報告ID供後續測試使用
                self.last_report_id = data.get('id')
                self.results['report_generation'] = True
                return True
            else:
                data = response.json()
                print_error(f"報告生成失敗: {data.get('error')}")
                return False
                
        except requests.Timeout:
            print_error("報告生成超時（AI生成需要較長時間）")
            print_info("  這可能是正常的，請稍後檢查報告列表")
            return False
        except Exception as e:
            print_error(f"報告生成異常: {e}")
            return False
    
    def test_report_list(self):
        """測試AI報告列表"""
        print_header("測試 3: AI 報告列表")
        
        try:
            print_info("獲取AI報告列表...")
            response = requests.get(f'{API_BASE}/ai/reports?type=market&limit=10', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                reports = data.get('reports', [])
                
                if len(reports) > 0:
                    print_success(f"獲取到 {len(reports)} 份報告")
                    
                    # 顯示最近3份報告
                    for i, report in enumerate(reports[:3]):
                        print_info(f"\n  報告 {i+1}:")
                        print_info(f"    ID: {report.get('id')}")
                        print_info(f"    標題: {report.get('title')}")
                        print_info(f"    情緒: {report.get('sentiment')}")
                        print_info(f"    生成時間: {report.get('created_at')}")
                        
                        # 顯示內容預覽
                        content_preview = report.get('content', '')[:150]
                        print_info(f"    內容預覽: {content_preview}...")
                    
                    if len(reports) > 3:
                        print_info(f"\n  ...還有 {len(reports) - 3} 份報告")
                    
                    self.results['report_list'] = True
                    return True
                else:
                    print_info("報告列表為空（尚未生成報告）")
                    return True
                    
            else:
                print_error(f"獲取報告列表失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"報告列表測試異常: {e}")
            return False
    
    def run_all_tests(self):
        """執行所有AI功能測試"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}AI 功能完整性測試{Colors.END}")
        print(f"{Colors.BOLD}測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # 測試1: AI連接
        connection_ok = self.test_connection()
        
        if not connection_ok:
            print_header("測試終止")
            print_error("AI連接失敗，無法繼續測試")
            print_info("請檢查:")
            print_info("  1. config/.env 中的 GOOGLE_AI_API_KEY 是否正確")
            print_info("  2. API伺服器是否已重啟")
            print_info("  3. 網路連接是否正常")
            return False
        
        # 等待1秒
        time.sleep(1)
        
        # 測試2: 報告生成
        self.test_report_generation()
        
        # 等待2秒
        time.sleep(2)
        
        # 測試3: 報告列表
        self.test_report_list()
        
        # 總結
        print_header("測試結果總結")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for v in self.results.values() if v)
        
        print(f"\n總測試數: {total_tests}")
        print_success(f"通過: {passed_tests}")
        
        if passed_tests < total_tests:
            print_error(f"失敗: {total_tests - passed_tests}")
            print("\n失敗項目:")
            for test, result in self.results.items():
                if not result:
                    print_error(f"  - {test}")
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n通過率: {pass_rate:.1f}%")
        
        if pass_rate == 100:
            print_success("\nAI功能狀態: 完美 ✨")
        elif pass_rate >= 75:
            print_success("\nAI功能狀態: 優秀 👍")
        elif pass_rate >= 50:
            print_info("\nAI功能狀態: 良好")
        else:
            print_error("\nAI功能狀態: 需要修復")
        
        print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
        
        return pass_rate >= 75

if __name__ == "__main__":
    tester = AIFunctionTester()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
