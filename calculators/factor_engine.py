"""
六大因子整合計算引擎

整合所有因子計算器，提供統一介面
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.value_factor import ValueFactorCalculator
from calculators.quality_factor import QualityFactorCalculator
from calculators.momentum_factor import MomentumFactorCalculator
from calculators.other_factors import SizeFactorCalculator, VolatilityFactorCalculator, GrowthFactorCalculator
from calculators.factor_base import FactorScoreStorage
from loguru import logger


class FactorEngine:
    """六大因子計算引擎"""
    
    def __init__(self):
        """初始化所有因子計算器"""
        self.value_calc = ValueFactorCalculator()
        self.quality_calc = QualityFactorCalculator()
        self.momentum_calc = MomentumFactorCalculator()
        self.size_calc = SizeFactorCalculator()
        self.volatility_calc = VolatilityFactorCalculator()
        self.growth_calc = GrowthFactorCalculator()
        self.storage = FactorScoreStorage()
    
    def calculate_all_factors(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw',
        save_to_db: bool = True
    ) -> dict:
        """
        計算所有六大因子
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場 ('tw' 或 'us')
            save_to_db: 是否儲存到資料庫
        
        Returns:
            因子分數字典
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"開始計算六大因子：{stock_code} @ {current_price}")
        logger.info(f"{'='*60}")
        
        scores = {}
        
        try:
            # 1. 價值因子
            scores['value'] = self.value_calc.calculate_value_score(
                stock_code, current_price, market
            )
            
            # 2. 品質因子
            scores['quality'] = self.quality_calc.calculate_quality_score(
                stock_code, market
            )
            
            # 3. 動能因子
            scores['momentum'] = self.momentum_calc.calculate_momentum_score(
                stock_code, market
            )
            
            # 4. 規模因子
            scores['size'] = self.size_calc.calculate_size_score(
                stock_code, current_price, market
            )
            
            # 5. 波動率因子
            scores['volatility'] = self.volatility_calc.calculate_volatility_score(
                stock_code, market
            )
            
            # 6. 成長因子
            scores['growth'] = self.growth_calc.calculate_growth_score(
                stock_code, market
            )
            
            # 計算總分
            valid_scores = [v for v in scores.values() if not pd.isna(v)]
            scores['total'] = sum(valid_scores) / len(valid_scores) if valid_scores else 50.0
            
            # 儲存到資料庫
            if save_to_db:
                self.storage.save_factor_scores(
                    stock_code=stock_code,
                    date=datetime.now().strftime('%Y-%m-%d'),
                    scores=scores,
                    market=market
                )
            
            logger.info(f"\n{'='*60}")
            logger.info(f"六大因子計算完成：{stock_code}")
            logger.info(f"{'='*60}")
            logger.info(f"價值: {scores['value']:.2f}")
            logger.info(f"品質: {scores['quality']:.2f}")
            logger.info(f"動能: {scores['momentum']:.2f}")
            logger.info(f"規模: {scores['size']:.2f}")
            logger.info(f"波動: {scores['volatility']:.2f}")
            logger.info(f"成長: {scores['growth']:.2f}")
            logger.info(f"總分: {scores['total']:.2f}")
            logger.info(f"{'='*60}\n")
            
            return scores
            
        except Exception as e:
            logger.error(f"計算因子失敗：{e}")
            return {
                'value': 50.0,
                'quality': 50.0,
                'momentum': 50.0,
                'size': 50.0,
                'volatility': 50.0,
                'growth': 50.0,
                'total': 50.0
            }
    
    def batch_calculate(
        self,
        stock_list: list,
        market: str = 'tw'
    ) -> pd.DataFrame:
        """
        批次計算多支股票的因子
        
        Args:
            stock_list: 股票代碼列表 [(code, price), ...]
            market: 市場
        
        Returns:
            因子分數 DataFrame
        """
        results = []
        
        for stock_code, current_price in stock_list:
            try:
                scores = self.calculate_all_factors(stock_code, current_price, market)
                scores['stock_code'] = stock_code
                scores['price'] = current_price
                results.append(scores)
            except Exception as e:
                logger.error(f"批次計算 {stock_code} 失敗：{e}")
                continue
        
        df = pd.DataFrame(results)
        
        # 按總分排序
        if not df.empty and 'total' in df.columns:
            df = df.sort_values('total', ascending=False)
        
        return df
    
    def close_all(self):
        """關閉所有資料庫連接"""
        self.value_calc.close()
        self.quality_calc.close()
        self.momentum_calc.close()
        self.size_calc.close()
        self.volatility_calc.close()
        self.growth_calc.close()
        self.storage.close()


# 使用範例
if __name__ == '__main__':
    engine = FactorEngine()
    
    try:
        # 單支股票測試
        scores = engine.calculate_all_factors(
            stock_code='2330',
            current_price=580.0,
            market='tw',
            save_to_db=True
        )
        
        print("\n六大因子分數：")
        for factor, score in scores.items():
            print(f"{factor:12}: {score:.2f}")
        
        # 批次測試
        print("\n\n批次計算測試：")
        stock_list = [
            ('2330', 580.0),  # 台積電
            ('2317', 120.0),  # 鴻海
            ('2454', 850.0),  # 聯發科
        ]
        
        df_results = engine.batch_calculate(stock_list, market='tw')
        print(df_results[['stock_code', 'value', 'quality', 'momentum', 'total']])
        
    finally:
        engine.close_all()
