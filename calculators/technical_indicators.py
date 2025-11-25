"""
技術指標計算器

提供常用技術指標計算功能：
- MA (移動平均線)
- EMA (指數移動平均線)
- MACD
- RSI
- 布林通道
- KD 指標
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


class TechnicalIndicators:
    """技術指標計算器"""
    
    @staticmethod
    def calculate_ma(
        prices: pd.Series,
        period: int = 20
    ) -> pd.Series:
        """
        計算移動平均線 (Moving Average)
        
        Args:
            prices: 價格序列
            period: 期間
        
        Returns:
            MA 序列
        """
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(
        prices: pd.Series,
        period: int = 12
    ) -> pd.Series:
        """
        計算指數移動平均線 (Exponential Moving Average)
        
        Args:
            prices: 價格序列
            period: 期間
        
        Returns:
            EMA 序列
        """
        return prices.ewm(span=period, adjust=False).mean()
    
    @classmethod
    def calculate_macd(
        cls,
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        計算 MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: 價格序列
            fast: 快線期間
            slow: 慢線期間
            signal: 訊號線期間
        
        Returns:
            (MACD, Signal, Histogram)
        """
        # 計算 EMA
        ema_fast = cls.calculate_ema(prices, fast)
        ema_slow = cls.calculate_ema(prices, slow)
        
        # MACD線
        macd_line = ema_fast - ema_slow
        
        # 訊號線
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # 柱狀圖
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_rsi(
        prices: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        計算 RSI (Relative Strength Index)
        
        Args:
            prices: 價格序列
            period: 期間
        
        Returns:
            RSI 序列
        """
        # 計算價格變動
        delta = prices.diff()
        
        # 分離漲跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 計算平均漲跌
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 計算 RS 和 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
   @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        計算布林通道 (Bollinger Bands)
        
        Args:
            prices: 價格序列
            period: 期間
            std_dev: 標準差倍數
        
        Returns:
            (上軌, 中軌, 下軌)
        """
        # 中軌（移動平均）
        middle_band = prices.rolling(window=period).mean()
        
        # 標準差
        std = prices.rolling(window=period).std()
        
        # 上軌和下軌
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_kd(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 9,
        k_period: int = 3,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        計算 KD 指標 (Stochastic Oscillator)
        
        Args:
            high: 最高價序列
            low: 最低價序列
            close: 收盤價序列
            period: 計算期間
            k_period: K 線平滑期間
            d_period: D 線平滑期間
        
        Returns:
            (K線, D線)
        """
        # 計算最高價和最低價
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        # RSV (Raw Stochastic Value)
        rsv = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # K 線
        k_line = rsv.ewm(span=k_period, adjust=False).mean()
        
        # D 線
        d_line = k_line.ewm(span=d_period, adjust=False).mean()
        
        return k_line, d_line
    
    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        計算 ATR (Average True Range)
        
        Args:
            high: 最高價序列
            low: 最低價序列
            close: 收盤價序列
            period: 期間
        
        Returns:
            ATR 序列
        """
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @classmethod
    def calculate_all_indicators(
        cls,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        計算所有技術指標
        
        Args:
            df: 包含 OHLCV 的 DataFrame
        
        Returns:
            包含所有指標的 DataFrame
        """
        result = df.copy()
        
        close_col = 'adjusted_close' if 'adjusted_close' in df.columns else 'close_price'
        high_col = 'high_price'
        low_col = 'low_price'
        
        try:
            # MA
            result['MA_5'] = cls.calculate_ma(df[close_col], 5)
            result['MA_10'] = cls.calculate_ma(df[close_col], 10)
            result['MA_20'] = cls.calculate_ma(df[close_col], 20)
            result['MA_60'] = cls.calculate_ma(df[close_col], 60)
            
            # EMA
            result['EMA_12'] = cls.calculate_ema(df[close_col], 12)
            result['EMA_26'] = cls.calculate_ema(df[close_col], 26)
            
            # MACD
            macd, signal, hist = cls.calculate_macd(df[close_col])
            result['MACD'] = macd
            result['MACD_Signal'] = signal
            result['MACD_Hist'] = hist
            
            # RSI
            result['RSI_14'] = cls.calculate_rsi(df[close_col], 14)
            
            # 布林通道
            upper, middle, lower = cls.calculate_bollinger_bands(df[close_col])
            result['BB_Upper'] = upper
            result['BB_Middle'] = middle
            result['BB_Lower'] = lower
            
            # KD
            k, d = cls.calculate_kd(
                df[high_col],
                df[low_col],
                df[close_col]
            )
            result['K'] = k
            result['D'] = d
            
            # ATR
            result['ATR'] = cls.calculate_atr(
                df[high_col],
                df[low_col],
                df[close_col]
            )
            
            logger.success("所有技術指標計算完成")
            
        except Exception as e:
            logger.error(f"計算技術指標失敗：{e}")
        
        return result


# 測試
if __name__ == '__main__':
    # 模擬資料
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    np.random.seed(42)
    
    df = pd.DataFrame({
        'trade_date': dates,
        'close_price': 100 + np.cumsum(np.random.randn(len(dates))),
        'high_price': 100 + np.cumsum(np.random.randn(len(dates))) + 2,
        'low_price': 100 + np.cumsum(np.random.randn(len(dates))) - 2,
        'volume': np.random.randint(1000000, 10000000, len(dates))
    })
    
    # 計算所有指標
    indicators = TechnicalIndicators()
    result = indicators.calculate_all_indicators(df)
    
    # 顯示結果
    print("=" * 60)
    print("技術指標計算測試")
    print("=" * 60)
    print(result[['trade_date', 'close_price', 'MA_20', 'RSI_14', 'MACD']].tail(10))
    print("=" * 60)
