"""
技術指標計算引擎
實現MA、RSI、MACD、Bollinger Bands等技術指標
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class TechnicalIndicators:
    """技術指標計算器"""
    
    @staticmethod
    def calculate_ma(prices: pd.Series, period: int = 20) -> pd.Series:
        """計算移動平均線 (MA)"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
        """計算指數移動平均線 (EMA)"""
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """計算相對強弱指標 (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices: pd.Series, 
                       fast: int = 12, 
                       slow: int = 26, 
                       signal: int = 9) -> Dict[str, pd.Series]:
        """計算MACD指標"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, 
                                   period: int = 20, 
                                   std_dev: int = 2) -> Dict[str, pd.Series]:
        """計算布林通道 (Bollinger Bands)"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': ma,
            'lower': lower_band
        }
    
    @staticmethod
    def calculate_atr(high: pd.Series, 
                      low: pd.Series, 
                      close: pd.Series, 
                      period: int = 14) -> pd.Series:
        """計算平均真實範圍 (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_kd(high: pd.Series, 
                     low: pd.Series, 
                     close: pd.Series, 
                     k_period: int = 9, 
                     d_period: int = 3) -> Dict[str, pd.Series]:
        """計算KD指標"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        rsv = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        
        return {
            'k': k,
            'd': d
        }
    
    @classmethod
    def calculate_all(cls, 
                      close: pd.Series, 
                      high: Optional[pd.Series] = None, 
                      low: Optional[pd.Series] = None) -> Dict:
        """計算所有技術指標"""
        indicators = {
            'ma_5': cls.calculate_ma(close, 5),
            'ma_20': cls.calculate_ma(close, 20),
            'ma_60': cls.calculate_ma(close, 60),
            'ema_12': cls.calculate_ema(close, 12),
            'ema_26': cls.calculate_ema(close, 26),
            'rsi_14': cls.calculate_rsi(close, 14),
            'macd': cls.calculate_macd(close),
            'bollinger': cls.calculate_bollinger_bands(close)
        }
        
        if high is not None and low is not None:
            indicators['atr_14'] = cls.calculate_atr(high, low, close, 14)
            indicators['kd'] = cls.calculate_kd(high, low, close)
        
        return indicators
