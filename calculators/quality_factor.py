"""
品質因子計算器 (Quality Factor Calculator)

計算指標：
- ROE (股東權益報酬率)
- ROA (資產報酬率)
- 負債權益比
- 毛利率穩定性
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.factor_base import FactorCalculatorBase
from loguru import logger


class QualityFactorCalculator(FactorCalculatorBase):
    """品質因子計算器"""
    
    def calculate_roe(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算 ROE (Return on Equity)
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            ROE (%)
        """
        # 獲取近四季淨利
        net_income_data = self.get_fundamental_data(stock_code, 'net_income', periods=4)
        
        # 獲取最新股東權益
        equity_data = self.get_fundamental_data(stock_code, 'shareholders_equity', periods=1)
        
        if net_income_data.empty or equity_data.empty:
            logger.warning(f"{stock_code}: 無 ROE 計算資料")
            return np.nan
        
        ttm_net_income = net_income_data['value'].sum()
        equity = equity_data['value'].iloc[0]
        
        if equity <= 0:
            return np.nan
        
        roe = (ttm_net_income / equity) * 100
        return roe
   
    def calculate_roa(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算 ROA (Return on Assets)
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            ROA (%)
        """
        # 獲取近四季淨利
        net_income_data = self.get_fundamental_data(stock_code, 'net_income', periods=4)
        
        # 獲取最新總資產
        assets_data = self.get_fundamental_data(stock_code, 'total_assets', periods=1)
        
        if net_income_data.empty or assets_data.empty:
            logger.warning(f"{stock_code}: 無 ROA 計算資料")
            return np.nan
        
        ttm_net_income = net_income_data['value'].sum()
        assets = assets_data['value'].iloc[0]
        
        if assets <= 0:
            return np.nan
        
        roa = (ttm_net_income / assets) * 100
        return roa
    
    def calculate_debt_to_equity(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算負債權益比 (Debt to Equity Ratio)
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            負債權益比
        """
        # 獲取最新負債
        debt_data = self.get_fundamental_data(stock_code, 'total_liabilities', periods=1)
        
        # 獲取最新股東權益
        equity_data = self.get_fundamental_data(stock_code, 'shareholders_equity', periods=1)
        
        if debt_data.empty or equity_data.empty:
            logger.warning(f"{stock_code}: 無負債權益比資料")
            return np.nan
        
        debt = debt_data['value'].iloc[0]
        equity = equity_data['value'].iloc[0]
        
        if equity <= 0:
            return np.nan
        
        debt_to_equity = debt / equity
        return debt_to_equity
    
    def calculate_gross_margin_stability(
        self,
        stock_code: str,
        market: str = 'tw',
        periods: int = 8
    ) -> float:
        """
        計算毛利率穩定性（變異係數的倒數）
        
        Args:
            stock_code: 股票代碼
            market: 市場
            periods: 觀察期數
        
        Returns:
            穩定性分數（越高越穩定）
        """
        # 獲取歷史毛利率
        margin_data = self.get_fundamental_data(stock_code, 'gross_margin', periods=periods)
        
        if len(margin_data) < 4:
            logger.warning(f"{stock_code}: 毛利率資料不足")
            return np.nan
        
        margins = margin_data['value']
        
        # 計算變異係數 (CV = std / mean)
        mean_margin = margins.mean()
        std_margin = margins.std()
        
        if mean_margin == 0:
            return np.nan
        
        cv = std_margin / abs(mean_margin)
        
        # 穩定性 = 1 / (1 + CV)
        # CV 越小，穩定性越高
        stability = 1 / (1 + cv)
        
        return stability * 100  # 轉為百分比
    
    def calculate_quality_score(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算綜合品質分數 (0-100)
        
        分數越高代表品質越好
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            品質分數
        """
        logger.info(f"計算品質因子：{stock_code}")
        
        # 計算各項指標
        roe = self.calculate_roe(stock_code, market)
        roa = self.calculate_roa(stock_code, market)
        debt_to_equity = self.calculate_debt_to_equity(stock_code, market)
        margin_stability = self.calculate_gross_margin_stability(stock_code, market)
        
        # 正規化分數
        roe_score = self.normalize_score(roe, 0, 30, invert=False)  # ROE 越高越好
        roa_score = self.normalize_score(roa, 0, 20, invert=False)  # ROA 越高越好
        debt_score = self.normalize_score(debt_to_equity, 0, 2, invert=True)  # 負債比越低越好
        stability_score = margin_stability if not pd.isna(margin_stability) else 50
        
        # 加權平均
        scores = []
        weights = []
        
        if not pd.isna(roe_score):
            scores.append(roe_score)
            weights.append(0.35)
        
        if not pd.isna(roa_score):
            scores.append(roa_score)
            weights.append(0.25)
        
        if not pd.isna(debt_score):
            scores.append(debt_score)
            weights.append(0.25)
        
        if not pd.isna(stability_score):
            scores.append(stability_score)
            weights.append(0.15)
        
        if not scores:
            return 50.0
        
        # 正規化權重
        weights = np.array(weights) / sum(weights)
        quality_score = np.average(scores, weights=weights)
        
        logger.info(f"{stock_code} 品質分數：{quality_score:.2f} (ROE:{roe:.2f}%, ROA:{roa:.2f}%, D/E:{debt_to_equity:.2f})")
        
        return quality_score
