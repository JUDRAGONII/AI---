"""
融資融券分析計算器 - Margin Analyzer
分析融資融券餘額變化與指標
"""
import pandas as pd
import numpy as np
from typing import Dict

class MarginAnalyzer:
    """融資融券分析器"""
    
    @staticmethod
    def analyze_margin_trading(margin_df: pd.DataFrame) -> Dict:
        """
        分析融資融券狀況
        
        Args:
            margin_df: DataFrame包含columns: trade_date, margin_balance, 
                      short_balance, margin_quota, short_quota
                      
        Returns:
            融資融券分析結果
        """
        if len(margin_df) < 20:
            return {'error': '數據不足'}
        
        recent = margin_df.iloc[-1]
        previous = margin_df.iloc[-20]
        
        # 融資使用率
        margin_usage = (recent['margin_balance'] / recent['margin_quota']) * 100 if recent['margin_quota'] > 0 else 0
        
        # 融券使用率
        short_usage = (recent['short_balance'] / recent['short_quota']) * 100 if recent['short_quota'] > 0 else 0
        
        # 融資變化
        margin_change = recent['margin_balance'] - previous['margin_balance']
        margin_change_pct = (margin_change / previous['margin_balance']) * 100 if previous['margin_balance'] > 0 else 0
        
        # 融券變化
        short_change = recent['short_balance'] - previous['short_balance']
        short_change_pct = (short_change / previous['short_balance']) * 100 if previous['short_balance'] > 0 else 0
        
        # 資券比（融資 / 融券）
        margin_short_ratio = recent['margin_balance'] / recent['short_balance'] if recent['short_balance'] > 0 else 999
        
        # 判斷訊號
        signal = MarginAnalyzer._interpret_margin_signal(
            margin_usage, short_usage, margin_change_pct, short_change_pct
        )
        
        return {
            'margin': {
                'balance': int(recent['margin_balance']),
                'quota': int(recent['margin_quota']),
                'usage_pct': round(margin_usage, 2),
                'change': int(margin_change),
                'change_pct': round(margin_change_pct, 2),
                'trend': '增加' if margin_change > 0 else '減少' if margin_change < 0 else '持平'
            },
            'short': {
                'balance': int(recent['short_balance']),
                'quota': int(recent['short_quota']),
                'usage_pct': round(short_usage, 2),
                'change': int(short_change),
                'change_pct': round(short_change_pct, 2),
                'trend': '增加' if short_change > 0 else '減少' if short_change < 0 else '持平'
            },
            'ratio': {
                'margin_short_ratio': round(margin_short_ratio, 2),
                'interpretation': '偏多' if margin_short_ratio > 5 else '偏空' if margin_short_ratio < 2 else '中性'
            },
            'signal': signal
        }
    
    @staticmethod
    def _interpret_margin_signal(
        margin_usage: float,
        short_usage: float,
        margin_change_pct: float,
        short_change_pct: float
    ) -> Dict:
        """解釋融資融券訊號"""
        
        warnings = []
        
        # 融資過高警示
        if margin_usage > 80:
            warnings.append('融資使用率過高，可能面臨斷頭風險')
        
        # 融券過高警示
        if short_usage > 80:
            warnings.append('融券使用率過高，可能面臨軋空風險')
        
        # 融資大增
        if margin_change_pct > 10:
            warnings.append('融資大幅增加，散戶追高跡象')
        
        # 融券大增
        if short_change_pct > 10:
            warnings.append('融券大幅增加，空方力量增強')
        
        # 綜合判斷
        if margin_change_pct > 5 and short_change_pct < -5:
            overall = '偏多但需注意融資風險'
        elif margin_change_pct < -5 and short_change_pct > 5:
            overall = '偏空壓力增加'
        elif margin_change_pct > 0 and short_change_pct > 0:
            overall = '多空對峙'
        else:
            overall = '中性觀望'
        
        return {
            'overall': overall,
            'warnings': warnings if warnings else ['無明顯警示'],
            'risk_level': '高' if len(warnings) >= 2 else '中' if len(warnings) == 1 else '低'
        }
    
    @staticmethod
    def calculate_margin_trend(margin_df: pd.DataFrame, window: int = 5) -> Dict:
        """
        計算融資融券趨勢
        
        Args:
            margin_df: 融資融券數據
            window: 移動平均窗口
            
        Returns:
            趨勢分析
        """
        margin_ma = margin_df['margin_balance'].rolling(window=window).mean()
        short_ma = margin_df['short_balance'].rolling(window=window).mean()
        
        margin_trend = 'up' if margin_ma.iloc[-1] > margin_ma.iloc[-window] else 'down'
        short_trend = 'up' if short_ma.iloc[-1] > short_ma.iloc[-window] else 'down'
        
        return {
            'margin_trend': '上升' if margin_trend == 'up' else '下降',
            'short_trend': '上升' if short_trend == 'up' else '下降',
            'divergence': margin_trend != short_trend
        }

# 測試函數
if __name__ == '__main__':
    # 生成測試數據
    from datetime import datetime
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    test_data = pd.DataFrame({
        'trade_date': dates,
        'margin_balance': np.random.randint(50000, 80000, 30),
        'margin_quota': 100000,
        'short_balance': np.random.randint(5000, 15000, 30),
        'short_quota': 20000
    })
    
    analyzer = MarginAnalyzer()
    result = analyzer.analyze_margin_trading(test_data)
    
    print("融資融券分析:")
    print(f"融資: {result['margin']}")
    print(f"融券: {result['short']}")
    print(f"資券比: {result['ratio']}")
    print(f"訊號: {result['signal']}")
