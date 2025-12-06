"""
技術指標計算器 - Technical Indicators
計算常用技術指標：RSI, MACD, KD, Williams %R, 布林通道等
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class TechnicalIndicators:
    """技術指標計算器"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        計算RSI（相對強弱指標）
        
        Args:
            prices: 價格序列
            period: 計算週期（預設14）
            
        Returns:
            RSI序列 (0-100)
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        計算MACD指標
        
        Args:
            prices: 價格序列
            fast: 快線週期
            slow: 慢線週期
            signal: 訊號線週期
            
        Returns:
            (MACD線, 訊號線, 柱狀圖)
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
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
        計算KD隨機指標
        
        Args:
            high: 最高價序列
            low: 最低價序列
            close: 收盤價序列
            period: RSV計算週期
            k_period: K值平滑週期
            d_period: D值平滑週期
            
        Returns:
            (K值, D值)
        """
        # 計算RSV
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        
        # 計算K值（RSV的移動平均）
        k = rsv.ewm(span=k_period, adjust=False).mean()
        
        # 計算D值（K值的移動平均）
        d = k.ewm(span=d_period, adjust=False).mean()
        
        return k, d
    
    @staticmethod
    def calculate_williams_r(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        計算威廉指標 (Williams %R)
        
        Args:
            high: 最高價序列
            low: 最低價序列
            close: 收盤價序列
            period: 計算週期
            
        Returns:
            Williams %R序列 (-100 to 0)
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        wr = (highest_high - close) / (highest_high - lowest_low) * -100
        return wr
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        計算布林通道
        
        Args:
            prices: 價格序列
            period: 移動平均週期
            std_dev: 標準差倍數
            
        Returns:
            (上軌, 中軌, 下軌)
        """
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_moving_averages(
        prices: pd.Series,
        periods: list = [5, 10, 20, 60, 120]
    ) -> Dict[str, pd.Series]:
        """
        計算多週期移動平均
        
        Args:
            prices: 價格序列
            periods: 週期列表
            
        Returns:
            {'ma5': Series, 'ma10': Series, ...}
        """
        mas = {}
        for period in periods:
            if len(prices) >= period:
                mas[f'ma{period}'] = prices.rolling(window=period).mean()
        return mas
    
    @staticmethod
    def get_signal_interpretation(indicator: str, value: float) -> Dict:
        """
        解釋技術指標訊號
        
        Args:
            indicator: 指標名稱 ('rsi', 'macd', 'kd', 'williams')
            value: 指標數值
            
        Returns:
            {
                'value': 數值,
                'signal': 訊號 ('超買'/'偏多'/'中性'/'偏空'/'超賣'),
                'action': 建議 ('賣出'/'減碼'/'持有'/'加碼'/'買入')
            }
        """
        if indicator == 'rsi':
            if value >= 80:
                signal, action = '極度超買', '賣出'
            elif value >= 70:
                signal, action = '超買', '減碼'
            elif value >= 50:
                signal, action = '偏多', '持有'
            elif value >= 30:
                signal, action = '偏空', '持有'
            elif value >= 20:
                signal, action = '超賣', '加碼'
            else:
                signal, action = '極度超賣', '買入'
        
        elif indicator == 'kd':
            if value >= 80:
                signal, action = '超買', '減碼'
            elif value >= 50:
                signal, action = '偏多', '持有'
            elif value >= 20:
                signal, action = '偏空', '持有'
            else:
                signal, action = '超賣', '加碼'
        
        elif indicator == 'williams':
            if value >= -20:
                signal, action = '超買', '減碼'
            elif value >= -50:
                signal, action = '偏多', '持有'
            elif value >= -80:
                signal, action = '偏空', '持有'
            else:
                signal, action = '超賣', '加碼'
        
        else:
            signal, action = '中性', '持有'
        
        return {
            'value': round(value, 2),
            'signal': signal,
            'action': action
        }

# 測試函數
if __name__ == '__main__':
    # 生成測試數據
    np.random.seed(42)
    test_data = pd.DataFrame({
        'close': np.cumsum(np.random.randn(100)) + 100,
        'high': np.cumsum(np.random.randn(100)) + 102,
        'low': np.cumsum(np.random.randn(100)) + 98
    })
    
    calculator = TechnicalIndicators()
    
    # 測試RSI
    rsi = calculator.calculate_rsi(test_data['close'])
    print("RSI:", rsi.tail(5))
    
    # 測試MACD
    macd, signal, hist = calculator.calculate_macd(test_data['close'])
    print("\nMACD:", macd.tail(3).values)
    
    # 測試KD
    k, d = calculator.calculate_kd(test_data['high'], test_data['low'], test_data['close'])
    print("\nKD - K:", k.tail(3).values)
    print("KD - D:", d.tail(3).values)
    
    # 訊號解釋
    interpretation = calculator.get_signal_interpretation('rsi', rsi.iloc[-1])
    print("\nRSI訊號解釋:", interpretation)
