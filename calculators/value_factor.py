"""
價值因子計算器 (Value Factor Calculator)

計算指標：
- P/E Ratio (本益比)
- P/B Ratio (股價淨值比)
- 股息殖利率 (Dividend Yield)
- EV/EBITDA
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.factor_base import FactorCalculatorBase
from loguru import logger


class ValueFactorCalculator(FactorCalculatorBase):
    """價值因子計算器"""
    
    def calculate_pe_ratio(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算本益比 (P/E Ratio)
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            P/E Ratio
        """
        # 獲取最新 EPS（近四季合計）
        eps_data = self.get_fundamental_data(stock_code, 'eps', periods=4)
        
        if eps_data.empty:
            logger.warning(f"{stock_code}: 無 EPS 資料")
            return np.nan
        
        # 計算 TTM EPS (Trailing Twelve Months)
        ttm_eps = eps_data['value'].sum()
        
        if ttm_eps <= 0:
            return np.nan
        
        pe_ratio = current_price / ttm_eps
        return pe_ratio
    
    def calculate_pb_ratio(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算股價淨值比 (P/B Ratio)
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            P/B Ratio
        """
        # 獲取最新每股淨值
        bvps_data = self.get_fundamental_data(stock_code, 'book_value_per_share', periods=1)
        
        if bvps_data.empty:
            logger.warning(f"{stock_code}: 無淨值資料")
            return np.nan
        
        book_value = bvps_data['value'].iloc[0]
        
        if book_value <= 0:
            return np.nan
        
        pb_ratio = current_price / book_value
        return pb_ratio
    
    def calculate_dividend_yield(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算股息殖利率 (Dividend Yield)
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            股息殖利率 (%)
        """
        # 獲取近一年配息
        dividend_data = self.get_fundamental_data(stock_code, 'dividend', periods=4)
        
        if dividend_data.empty:
            return np.nan
        
        annual_dividend = dividend_data['value'].sum()
        
        if current_price <= 0:
            return np.nan
        
        dividend_yield = (annual_dividend / current_price) * 100
        return dividend_yield
    
    def calculate_ev_ebitda(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算 EV/EBITDA
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            EV/EBITDA
        """
        # 簡化版本：使用市值代替 EV
        # 實際應用需要加入負債、現金等
        
        # 獲取股本數
        shares_data = self.get_fundamental_data(stock_code, 'shares_outstanding', periods=1)
        
        if shares_data.empty:
            return np.nan
        
        shares = shares_data['value'].iloc[0]
        market_cap = current_price * shares
        
        # 獲取 EBITDA
        ebitda_data = self.get_fundamental_data(stock_code, 'ebitda', periods=4)
        
        if ebitda_data.empty:
            return np.nan
        
        ttm_ebitda = ebitda_data['value'].sum()
        
        if ttm_ebitda <= 0:
            return np.nan
        
        ev_ebitda = market_cap / ttm_ebitda
        return ev_ebitda
    
    def calculate_value_score(
        self,
        stock_code: str,
        current_price: float,
        market: str = 'tw'
    ) -> float:
        """
        計算綜合價值分數 (0-100)
        
        分數越高代表越便宜（價值型）
        
        Args:
            stock_code: 股票代碼
            current_price: 當前股價
            market: 市場
        
        Returns:
            價值分數
        """
        logger.info(f"計算價值因子：{stock_code}")
        
        # 計算各項指標
        pe = self.calculate_pe_ratio(stock_code, current_price, market)
        pb = self.calculate_pb_ratio(stock_code, current_price, market)
        dy = self.calculate_dividend_yield(stock_code, current_price, market)
        ev_ebitda = self.calculate_ev_ebitda(stock_code, current_price, market)
        
        # 正規化分數（值越低越好，所以 invert=True）
        pe_score = self.normalize_score(pe, 5, 30, invert=True)
        pb_score = self.normalize_score(pb, 0.5, 5, invert=True)
        dy_score = self.normalize_score(dy, 0, 10, invert=False)  # 殖利率越高越好
        ev_ebitda_score = self.normalize_score(ev_ebitda, 3, 20, invert=True)
        
        # 加權平均
        scores = []
        weights = []
        
        if not pd.isna(pe_score):
            scores.append(pe_score)
            weights.append(0.3)
        
        if not pd.isna(pb_score):
            scores.append(pb_score)
            weights.append(0.3)
        
        if not pd.isna(dy_score):
            scores.append(dy_score)
            weights.append(0.2)
        
        if not pd.isna(ev_ebitda_score):
            scores.append(ev_ebitda_score)
            weights.append(0.2)
        
        if not scores:
            return 50.0  # 無資料時給予中間分數
        
        # 正規化權重
        weights = np.array(weights) / sum(weights)
        value_score = np.average(scores, weights=weights)
        
        logger.info(f"{stock_code} 價值分數：{value_score:.2f} (PE:{pe:.2f}, PB:{pb:.2f}, DY:{dy:.2f}%)")
        
        return value_score
