"""
綜合因子計算器
整合所有六大因子計算
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.factor_base import FactorCalculatorBase
from loguru import logger


class SizeFactorCalculator(FactorCalculatorBase):
    """規模因子計算器"""
    
    def calculate_market_cap(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算市值
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            市值（億）
        """
        # 獲取股本數
        shares_data = self.get_fundamental_data(stock_code, 'shares_outstanding', periods=1)
        
        if shares_data.empty:
            logger.warning(f"{stock_code}: 無股本資料")
            return np.nan
        
        shares = shares_data['value'].iloc[0]
        market_cap = (current_price * shares) / 100000000  # 轉為億
        
        return market_cap
    
    def calculate_size_score(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算規模分數
        
        台股：
        - 大型股 (>500億): 70-100分
        - 中型股 (100-500億): 40-70分
        - 小型股 (<100億): 0-40分
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            規模分數
        """
        logger.info(f"計算規模因子：{stock_code}")
        
        market_cap = self.calculate_market_cap(stock_code, current_price, market)
        
        if pd.isna(market_cap):
            return 50.0
        
        # 台股規模分級
        if market == 'tw':
            size_score = self.normalize_score(market_cap, 10, 1000, invert=False)
        else:  # 美股
            size_score = self.normalize_score(market_cap, 100, 10000, invert=False)
        
        logger.info(f"{stock_code} 規模分數：{size_score:.2f} (市值:{market_cap機.2f}億)")
        
        return size_score


class VolatilityFactorCalculator(FactorCalculatorBase):
    """波動率因子計算器"""
    
    def calculate_volatility_score(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算波動率分數
        
        波動率越低，分數越高（代表風險越低）
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            波動率分數
        """
        logger.info(f"計算波動率因子：{stock_code}")
        
        # 獲取一年價格資料
        end_date = datetime.now().strftime('%Y-%m-%d')
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
        
        prices = self.get_stock_prices(stock_code, start_date, end_date, market)
        
        if prices.empty:
            return 50.0
        
        # 計算年化波動率
        volatility = self.calculate_volatility(prices, window=252)
        
        if pd.isna(volatility):
            return 50.0
        
        # 正規化（波動率越低越好）
        volatility_pct = volatility * 100  # 轉為百分比
        vol_score = self.normalize_score(volatility_pct, 10, 50, invert=True)
        
        logger.info(f"{stock_code} 波動率分數：{vol_score:.2f} (年化波動:{volatility_pct:.2f}%)")
        
        return vol_score


class GrowthFactorCalculator(FactorCalculatorBase):
    """成長因子計算器"""
    
    def calculate_revenue_cagr(
        self,
        stock_code: str,
        periods: int = 12,
        market: str = 'tw'
    ) -> float:
        """
        計算營收 CAGR (Compound Annual Growth Rate)
        
        Args:
            stock_code: 股票代碼
            periods: 期數（季度）
            market: 市場
        
        Returns:
            營收 CAGR (%)
        """
        # 獲取歷史營收
        revenue_data = self.get_fundamental_data(stock_code, 'revenue', periods=periods)
        
        if len(revenue_data) < periods:
            logger.warning(f"{stock_code}: 營收資料不足")
            return np.nan
        
        # 計算 CAGR
        start_revenue = revenue_data['value'].iloc[-1]  # 最早
        end_revenue = revenue_data['value'].iloc[0]  # 最新
        years = periods / 4  # 轉為年數
        
        cagr = self.calculate_cagr(start_revenue, end_revenue, years)
        
        return cagr * 100  # 轉為百分比
    
    def calculate_eps_cagr(
        self,
        stock_code: str,
        periods: int = 12,
        market: str = 'tw'
    ) -> float:
        """
        計算 EPS CAGR
        
        Args:
            stock_code: 股票代碼
            periods: 期數（季度）
            market: 市場
        
        Returns:
            EPS CAGR (%)
        """
        # 獲取歷史 EPS
        eps_data = self.get_fundamental_data(stock_code, 'eps', periods=periods)
        
        if len(eps_data) < periods:
            logger.warning(f"{stock_code}: EPS 資料不足")
            return np.nan
        
        # 計算年度 EPS（每4季加總）
        eps_annual = []
        for i in range(0, len(eps_data), 4):
            if i + 4 <= len(eps_data):
                annual_eps = eps_data['value'].iloc[i:i+4].sum()
                eps_annual.append(annual_eps)
        
        if len(eps_annual) < 2:
            return np.nan
        
        # 計算 CAGR
        start_eps = eps_annual[-1]
        end_eps = eps_annual[0]
        years = len(eps_annual) - 1
        
        cagr = self.calculate_cagr(start_eps, end_eps, years)
        
        return cagr * 100
    
    def calculate_growth_score(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算綜合成長分數
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            成長分數
        """
        logger.info(f"計算成長因子：{stock_code}")
        
        # 計算各項指標
        revenue_cagr = self.calculate_revenue_cagr(stock_code, periods=12, market=market)
        eps_cagr = self.calculate_eps_cagr(stock_code, periods=12, market=market)
        
        # 正規化分數
        rev_score = self.normalize_score(revenue_cagr, -10, 30, invert=False)
        eps_score = self.normalize_score(eps_cagr, -10, 30, invert=False)
        
        # 加權平均
        scores = []
        weights = []
        
        if not pd.isna(rev_score):
            scores.append(rev_score)
            weights.append(0.5)
        
        if not pd.isna(eps_score):
            scores.append(eps_score)
            weights.append(0.5)
        
        if not scores:
            return 50.0
        
        weights = np.array(weights) / sum(weights)
        growth_score = np.average(scores, weights=weights)
        
        logger.info(f"{stock_code} 成長分數：{growth_score:.2f} (營收CAGR:{revenue_cagr:.2f}%, EPS CAGR:{eps_cagr:.2f}%)")
        
        return growth_score
