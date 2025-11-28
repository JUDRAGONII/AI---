"""
因子計算引擎
實現價值、品質、動能、規模、波動率、成長等六大因子
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional

class FactorCalculator:
    """因子計算器"""
    
    @staticmethod
    def calculate_value_factors(market_cap: float, 
                                 price: float, 
                                 book_value: float, 
                                 earnings: float, 
                                 dividend: float) -> Dict[str, float]:
        """計算價值因子"""
        pe_ratio = price / earnings if earnings > 0 else None
        pb_ratio = price / book_value if book_value > 0 else None
        dividend_yield = (dividend / price * 100) if price > 0 else None
        
        return {
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'dividend_yield': dividend_yield
        }
    
    @staticmethod
    def calculate_quality_factors(total_assets: float, 
                                   total_equity: float, 
                                   total_liabilities: float, 
                                   net_income: float, 
                                   revenue: float) -> Dict[str, float]:
        """計算品質因子"""
        roe = (net_income / total_equity * 100) if total_equity > 0 else None
        roa = (net_income / total_assets * 100) if total_assets > 0 else None
        debt_to_equity = (total_liabilities / total_equity) if total_equity > 0 else None
        net_margin = (net_income / revenue * 100) if revenue > 0 else None
        
        return {
            'roe': roe,
            'roa': roa,
            'debt_to_equity': debt_to_equity,
            'net_margin': net_margin
        }
    
    @staticmethod
    def calculate_momentum_factors(prices: pd.Series, 
                                    market_prices: Optional[pd.Series] = None) -> Dict:
        """計算動能因子"""
        # RSI-14
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 相對報酬率
        stock_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100 if len(prices) > 0 else None
        
        # 距52週高點距離
        high_52w = prices.rolling(252).max()
        distance_from_high = ((prices - high_52w) / high_52w * 100)
        
        result = {
            'rsi_14': rsi.iloc[-1] if len(rsi) > 0 else None,
            'return_1m': stock_return,
            'distance_from_52w_high': distance_from_high.iloc[-1] if len(distance_from_high) > 0 else None
        }
        
        if market_prices is not None and len(market_prices) == len(prices):
            market_return = (market_prices.iloc[-1] / market_prices.iloc[0] - 1) * 100
            relative_return = stock_return - market_return
            result['relative_return'] = relative_return
        
        return result
    
    @staticmethod
    def calculate_size_factor(market_cap: float) -> Dict[str, float]:
        """計算規模因子"""
        return {
            'market_cap': market_cap,
            'log_market_cap': np.log(market_cap) if market_cap > 0 else None
        }
    
    @staticmethod
    def calculate_volatility_factor(prices: pd.Series, period: int = 252) -> Dict[str, float]:
        """計算波動率因子"""
        returns = prices.pct_change().dropna()
        
        historical_vol = returns.std() * np.sqrt(period) * 100 if len(returns) > 0 else None
        
        return {
            'historical_volatility': historical_vol
        }
    
    @staticmethod
    def calculate_growth_factors(revenue_history: pd.Series, 
                                  eps_history: pd.Series) -> Dict[str, float]:
        """計算成長因子"""
        def calculate_cagr(series: pd.Series) -> Optional[float]:
            if len(series) < 2:
                return None
            years = len(series) - 1
            if series.iloc[0] <= 0:
                return None
            cagr = (pow(series.iloc[-1] / series.iloc[0], 1/years) - 1) * 100
            return cagr
        
        revenue_cagr = calculate_cagr(revenue_history)
        eps_cagr = calculate_cagr(eps_history)
        
        return {
            'revenue_cagr': revenue_cagr,
            'eps_cagr': eps_cagr
        }
