"""
動能因子計算器 (Momentum Factor Calculator)

計算指標：
- RSI-14
- 相對大盤報酬率
- 距 52 週高點距離
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.factor_base import FactorCalculatorBase
from loguru import logger


class MomentumFactorCalculator(FactorCalculatorBase):
    """動能因子計算器"""
    
    def calculate_rsi(
        self,
        prices: pd.DataFrame,
        period: int = 14
    ) -> float:
        """
        計算 RSI (Relative Strength Index)
        
        Args:
            prices: 價格 DataFrame
            period: RSI 期間（預設 14）
        
        Returns:
            RSI 值 (0-100)
        """
        if len(prices) < period + 1:
            logger.warning("資料不足，無法計算 RSI")
            return np.nan
        
        close_col = 'adjusted_close' if 'adjusted_close' in prices.columns else 'close_price'
        closes = prices[close_col]
        
        # 計算價格變動
        delta = closes.diff()
        
        # 分離漲跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 計算平均漲跌
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 計算 RS 和 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 返回最新值
        return rsi.iloc[-1]
    
    def calculate_relative_return(
        self,
        stock_code: str,
        period_days: int = 252,
        market: str = 'tw'
    ) -> float:
        """
        計算相對大盤報酬率
        
        Args:
            stock_code: 股票代碼
            period_days: 計算期間（天數）
            market: 市場
        
        Returns:
            相對報酬率 (%)
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=period_days + 30)).strftime('%Y-%m-%d')
        
        # 獲取股票價格
        stock_prices = self.get_stock_prices(stock_code, start_date, end_date, market)
        
        if stock_prices.empty or len(stock_prices) < period_days:
            logger.warning(f"{stock_code}: 資料不足")
            return np.nan
        
        # 計算股票報酬ὡ��
        close_col = 'adjusted_close' if 'adjusted_close' in stock_prices.columns else 'close_price'
        stock_return = (stock_prices[close_col].iloc[-1] / stock_prices[close_col].iloc[0] - 1) * 100
        
        # 獲取大盤指數（簡化：使用固定值或從資料庫獲取）
        # 實際應該根據 market 獲取對應指數（如 ^TWII 或 ^GSPC）
        market_return = 10.0  # 假設值，實際應從資料庫計算
        
        # 相對報酬 = 股票報酬 - 大盤報酬
        relative_return = stock_return - market_return
        
        return relative_return
    
    def calculate_distance_from_52w_high(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算股價距 52 週高點的距離
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            距離百分比（負值表示低於高點）
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 獲取52週價格
        prices = self.get_stock_prices(stock_code, start_date, end_date, market)
        
        if prices.empty:
            logger.warning(f"{stock_code}: 無52週資料")
            return np.nan
        
        close_col = 'adjusted_close' if 'adjusted_close' in prices.columns else 'close_price'
        
        # 找出52週最高價
        high_52w = prices[close_col].max()
        current_price = prices[close_col].iloc[-1]
        
        # 計算距離百分比
        distance = ((current_price / high_52w) - 1) * 100
        
        return distance
    
    def calculate_momentum_score(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> float:
        """
        計算綜合動能分數 (0-100)
        
        分數越高代表動能越強
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            動能分數
        """
        logger.info(f"計算動能因子：{stock_code}")
        
        # 獲取價格資料
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
        prices = self.get_stock_prices(stock_code, start_date, end_date, market)
        
        if prices.empty:
            return 50.0
        
        # 計算各項指標
        rsi = self.calculate_rsi(prices, period=14)
        relative_return = self.calculate_relative_return(stock_code, period_days=252, market=market)
        distance_52w = self.calculate_distance_from_52w_high(stock_code, market)
        
        # 正規化分數
        rsi_score = self.normalize_score(rsi, 30, 70, invert=False)  # RSI 50-70 較佳
        return_score = self.normalize_score(relative_return, -20, 50, invert=False)  # 相對報酬越高越好
        distance_score = self.normalize_score(distance_52w, -30, 0, invert=False)  # 接近高點越好
        
        # 加權平均
        scores = []
        weights = []
        
        if not pd.isna(rsi_score):
            scores.append(rsi_score)
            weights.append(0.3)
        
        if not pd.isna(return_score):
            scores.append(return_score)
            weights.append(0.4)
        
        if not pd.isna(distance_score):
            scores.append(distance_score)
            weights.append(0.3)
        
        if not scores:
            return 50.0
        
        # 正規化權重
        weights = np.array(weights) / sum(weights)
        momentum_score = np.average(scores, weights=weights)
        
        logger.info(f"{stock_code} 動能分數：{momentum_score:.2f} (RSI:{rsi:.2f}, 相對報酬:{relative_return:.2f}%)")
        
        return momentum_score
