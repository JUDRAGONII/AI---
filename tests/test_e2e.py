"""
端到端測試腳本
測試系統所有核心功能
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from api_clients.tw_stock_client import TWStockClient
from api_clients.us_stock_client import USStockClient
from api_clients.gold_client import GoldClient
from api_clients.exchange_rate_client import ExchangeRateClient
from api_clients.macro_client import MacroClient
from api_clients.news_client import NewsClient
from calculators.technical_indicators import TechnicalIndicatorCalculator
from calculators.quant_factors import QuantFactorCalculator
import pandas as pd
import numpy as np


class SystemTest:
    """系統端到端測試"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test(self, test_name: str, test_func):
        """執行單一測試"""
        try:
            logger.info(f"\n▶️  測試：{test_name}")
            test_func()
            self.passed += 1
            logger.success(f"✅ {test_name} - 通過")
            return True
        except Exception as e:
            self.failed += 1
            self.errors.append((test_name, str(e)))
            logger.error(f"❌ {test_name} - 失敗: {e}")
            return False
    
    def test_tw_stock_client(self):
        """測試台股客戶端"""
        client = TWStockClient()
        
        # 測試取得台積電資料
        df = client.get_daily_price('2330', '2024-11-01', '2024-11-22')
        assert not df.empty, "台積電資料為空"
        assert 'close' in df.columns, "缺少收盤價欄位"
        logger.info(f"   取得 {len(df)} 筆台積電資料")
    
    def test_us_stock_client(self):
        """測試美股客戶端"""
        client = USStockClient()
        
        # 測試取得 Apple 資料
        df = client.get_daily_price('AAPL', '2024-11-01', '2024-11-22')
        assert not df.empty, "Apple 資料為空"
        assert 'close' in df.columns, "缺少收盤價欄位"
        logger.info(f"   取得 {len(df)} 筆 Apple 資料")
        
        # 測試取得公司資訊
        info = client.get_company_info('AAPL')
        assert 'company_name' in info, "缺少公司名稱"
        logger.info(f"   公司名稱：{info.get('company_name', 'N/A')}")
    
    def test_gold_client(self):
        """測試黃金價格客戶端"""
        client = GoldClient()
        
        # 測試取得黃金價格
        df = client.get_daily_price('2024-11-01', '2024-11-22')
        assert not df.empty, "黃金價格資料為空"
        logger.info(f"   取得 {len(df)} 筆黃金價格")
    
    def test_exchange_rate_client(self):
        """測試匯率客戶端"""
        client = ExchangeRateClient()
        
        # 測試取得匯率
        rate = client.get_historical_rate('USD', 'TWD', '2024-11-22')
        assert rate is not None, "匯率為空"
        assert rate > 0, "匯率數值異常"
        logger.info(f"   USD/TWD 匯率：{rate:.2f}")
    
    def test_macro_client(self):
        """測試宏觀經濟客戶端"""
        client = MacroClient()
        
        # 測試取得 GDP 資料
        df = client.get_indicator('GDP', '2023-01-01', '2024-01-01')
        assert not df.empty, "GDP 資料為空"
        logger.info(f"   取得 {len(df)} 筆 GDP 資料")
    
    def test_news_client(self):
        """測試金融新聞客戶端"""
        client = NewsClient()
        
        # 測試取得新聞
        news = client.get_market_news(limit=5)
        assert len(news) > 0, "新聞資料為空"
        logger.info(f"   取得 {len(news)} 則新聞")
        
        # 顯示第一則標題
        if news:
            logger.info(f"   最新：{news[0]['title'][:50]}...")
    
    def test_technical_indicators(self):
        """測試技術指標計算"""
        # 生成測試資料
        dates = pd.date_range('2024-01-01', periods=100)
        test_data = pd.DataFrame({
            'trade_date': dates,
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, 100)
        })
        
        calc = TechnicalIndicatorCalculator()
        indicators = calc.calculate_all_indicators(test_data)
        
        assert not indicators.empty, "技術指標計算結果為空"
        assert 'ma_20' in indicators.columns, "缺少 MA20 欄位"
        assert 'rsi_14' in indicators.columns, "缺少 RSI14 欄位"
        assert 'macd' in indicators.columns, "缺少 MACD 欄位"
        
        logger.info(f"   計算 {len(indicators.columns)} 個技術指標")
    
    def test_quant_factors(self):
        """測試量化因子計算"""
        # 生成測試資料
        test_data = pd.DataFrame({
            'pe_ratio': [15.2, 22.5, 10.8, 30.1, 18.3],
            'pb_ratio': [2.1, 3.5, 1.2, 4.8, 2.5],
            'dividend_yield': [0.025, 0.015, 0.040, 0.010, 0.030],
            'roe': [0.15, 0.10, 0.20, 0.08, 0.12],
            'roa': [0.08, 0.05, 0.12, 0.04, 0.07],
        })
        
        calc = QuantFactorCalculator()
        value_score, _ = calc.calculate_value_score(test_data)
        quality_score, _ = calc.calculate_quality_score(test_data)
        
        assert len(value_score) == len(test_data), "價值因子分數數量錯誤"
        assert len(quality_score) == len(test_data), "品質因子分數數量錯誤"
        assert value_score.min() >= 0, "分數不應為負"
        assert value_score.max() <= 100, "分數不應超過100"
        
        logger.info(f"   價值因子平均分數：{value_score.mean():.2f}")
        logger.info(f"   品質因子平均分數：{quality_score.mean():.2f}")
    
    def run_all_tests(self):
        """執行所有測試"""
        logger.info("=" * 70)
        logger.info("🧪 專業金融資料庫系統端到端測試")
        logger.info("=" * 70)
        
        start_time = time.time()
        
        # API 客戶端測試
        logger.info("\n【第1組】API 客戶端測試")
        self.run_test("台股客戶端", self.test_tw_stock_client)
        time.sleep(1)
        self.run_test("美股客戶端", self.test_us_stock_client)
        time.sleep(1)
        self.run_test("黃金價格客戶端", self.test_gold_client)
        time.sleep(1)
        self.run_test("匯率客戶端", self.test_exchange_rate_client)
        time.sleep(1)
        self.run_test("宏觀經濟客戶端", self.test_macro_client)
        time.sleep(1)
        self.run_test("金融新聞客戶端", self.test_news_client)
        
        # 計算模組測試
        logger.info("\n【第2組】計算模組測試")
        self.run_test("技術指標計算", self.test_technical_indicators)
        self.run_test("量化因子計算", self.test_quant_factors)
        
        # 計算執行時間
        elapsed = time.time() - start_time
        
        # 輸出總結
        logger.info("\n" + "=" * 70)
        logger.info("📊 測試結果總結")
        logger.info("=" * 70)
        logger.info(f"✅ 通過：{self.passed} 項")
        logger.info(f"❌ 失敗：{self.failed} 項")
        logger.info(f"⏱️  執行時間：{elapsed:.1f} 秒")
        
        if self.failed > 0:
            logger.info("\n失敗詳情：")
            for test_name, error in self.errors:
                logger.error(f"  - {test_name}: {error}")
        
        logger.info("=" * 70)
        
        if self.failed == 0:
            logger.success("\n🎉 所有測試通過！系統運作正常")
            return 0
        else:
            logger.warning(f"\n⚠️  有 {self.failed} 項測試失敗，請檢查")
            return 1


def main():
    tester = SystemTest()
    return tester.run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
