"""
位階分析計算器 - Position Analyzer
計算股價在歷史區間的相對位置、趨勢強度、多空判斷
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class PositionAnalyzer:
    """股價位階分析計算器"""
    
    @staticmethod
    def calculate_position_level(prices: pd.Series) -> Dict:
        """
        計算價格位階（相對52週高低點）
        
        Args:
            prices: 價格序列（至少252個交易日）
            
        Returns:
            {
                'current_price': 當前價格,
                'high_52w': 52週最高價,
                'low_52w': 52週最低價,
                'percentile_52w': 當前價格在52週範圍的百分位 (0-100),
                'level': 位階描述 ('低檔區'/'中檔區'/'高檔區'),
                'distance_from_high': 距離高點的百分比,
                'distance_from_low': 距離低點的百分比
            }
        """
        if len(prices) < 252:
            # 使用所有可用數據
            high_52w = prices.max()
            low_52w = prices.min()
        else:
            # 使用最近252個交易日（約1年）
            recent_prices = prices.tail(252)
            high_52w = recent_prices.max()
            low_52w = recent_prices.min()
        
        current_price = prices.iloc[-1]
        
        # 計算百分位
        if high_52w == low_52w:
            percentile = 50.0
        else:
            percentile = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        
        # 判斷位階
        if percentile >= 70:
            level = '高檔區'
        elif percentile <= 30:
            level = '低檔區'
        else:
            level = '中檔區'
        
        # 距離高低點的百分比
        distance_from_high = ((high_52w - current_price) / current_price) * 100
        distance_from_low = ((current_price - low_52w) / current_price) * 100
        
        return {
            'current_price': float(current_price),
            'high_52w': float(high_52w),
            'low_52w': float(low_52w),
            'percentile_52w': round(percentile, 2),
            'level': level,
            'distance_from_high': round(distance_from_high, 2),
            'distance_from_low': round(distance_from_low, 2)
        }
    
    @staticmethod
    def analyze_trend(prices: pd.Series, periods: List[int] = [5, 20, 60]) -> Dict:
        """
        分析價格趨勢（使用移動平均）
        
        Args:
            prices: 價格序列
            periods: 移動平均週期列表
            
        Returns:
            {
                'trend': 趨勢描述 ('強勢上升'/'上升'/'盤整'/'下降'/'強勢下降'),
                'ma_alignment': MA排列狀態,
                'slope': 趨勢斜率,
                'strength': 趨勢強度 (0-100)
            }
        """
        current_price = prices.iloc[-1]
        
        # 計算各週期MA
        mas = {}
        for period in periods:
            if len(prices) >= period:
                mas[f'ma{period}'] = prices.tail(period).mean()
        
        # 判斷MA排列（多頭/空頭）
        if len(mas) >= 3:
            ma_values = list(mas.values())
            is_bullish = all(ma_values[i] > ma_values[i+1] for i in range(len(ma_values)-1))
            is_bearish = all(ma_values[i] < ma_values[i+1] for i in range(len(ma_values)-1))
            
            if is_bullish and current_price > ma_values[0]:
                ma_alignment = '完美多頭排列'
            elif is_bearish and current_price < ma_values[0]:
                ma_alignment = '完美空頭排列'
            elif current_price > ma_values[0]:
                ma_alignment = '偏多'
            else:
                ma_alignment = '偏空'
        else:
            ma_alignment = '數據不足'
        
        # 計算趨勢斜率（使用20日MA）
        if len(prices) >= 20:
            ma20 = prices.rolling(window=20).mean()
            slope = (ma20.iloc[-1] - ma20.iloc[-10]) / ma20.iloc[-10] * 100
        else:
            slope = 0
        
        # 趨勢強度（基於斜率和價格與MA的關係）
        strength = min(abs(slope) * 10, 100)
        
        # 判斷趨勢
        if slope > 5 and ma_alignment in ['完美多頭排列', '偏多']:
            trend = '強勢上升'
        elif slope > 0:
            trend = '上升趨勢'
        elif slope > -5:
            trend = '盤整'
        elif slope > -10:
            trend = '下降趨勢'
        else:
            trend = '強勢下降'
        
        return {
            'trend': trend,
            'ma_alignment': ma_alignment,
            'slope': round(slope, 2),
            'strength': round(strength, 2),
            'current_vs_ma5': round((current_price / mas.get('ma5', current_price) - 1) * 100, 2) if 'ma5' in mas else 0,
            'current_vs_ma20': round((current_price / mas.get('ma20', current_price) - 1) * 100, 2) if 'ma20' in mas else 0
        }
    
    @staticmethod
    def analyze_volume_price_relation(prices: pd.Series, volumes: pd.Series, window: int = 20) -> Dict:
        """
        分析量價關係
        
        Args:
            prices: 價格序列
            volumes: 成交量序列
            window: 分析窗口
            
        Returns:
            {
                'relation': 量價關係 ('價漲量增'/'價漲量縮'/'價跌量增'/'價跌量縮'),
                'signal': 訊號判斷 ('正常'/'警示'/'背離'),
                'volume_vs_avg': 當前量與平均量的比較百分比
            }
        """
        if len(prices) < window or len(volumes) < window:
            return {
                'relation': '數據不足',
                'signal': '無法判斷',
                'volume_vs_avg': 0
            }
        
        # 計算價格和成交量變化
        price_change = (prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2]
        volume_avg = volumes.tail(window).mean()
        current_volume = volumes.iloc[-1]
        volume_change = (current_volume - volume_avg) / volume_avg
        
        # 判斷量價關係
        if price_change > 0 and volume_change > 0:
            relation = '價漲量增'
            signal = '正常' if volume_change > 0.2 else '警示'
        elif price_change > 0 and volume_change < 0:
            relation = '價漲量縮'
            signal = '背離'
        elif price_change < 0 and volume_change > 0:
            relation = '價跌量增'
            signal = '警示'
        elif price_change < 0 and volume_change < 0:
            relation = '價跌量縮'
            signal = '正常'
        else:
            relation = '盤整'
            signal = '正常'
        
        return {
            'relation': relation,
            'signal': signal,
            'volume_vs_avg': round(volume_change * 100, 2)
        }
    
    @staticmethod
    def comprehensive_judgment(
        position_level: Dict,
        trend: Dict,
        volume_price: Dict,
        technical_signals: Optional[Dict] = None
    ) -> Dict:
        """
        綜合判斷（整合各項分析）
        
        Args:
            position_level: 位階分析結果
            trend: 趨勢分析結果
            volume_price: 量價關係結果
            technical_signals: 技術指標訊號（可選）
            
        Returns:
            {
                'recommendation': 建議 ('多頭強勢'/'偏多持有'/'中性觀望'/'偏空減碼'/'空頭續弱'),
                'confidence': 信心度 ('高'/'中'/'低'),
                'score': 綜合評分 (0-100),
                'reasons': 判斷理由列表
            }
        """
        score = 50  # 基準分數
        reasons = []
        
        # 位階評分（30%權重）
        if position_level['level'] == '低檔區':
            score += 15
            reasons.append('價格處於低檔區，具備反彈空間')
        elif position_level['level'] == '高檔區':
            score -= 15
            reasons.append('價格處於高檔區，注意回檔風險')
        
        # 趨勢評分（40%權重）
        if trend['trend'] in ['強勢上升', '上升趨勢']:
            score += 20
            reasons.append(f"{trend['trend']}，動能強勁")
        elif trend['trend'] in ['強勢下降', '下降趨勢']:
            score -= 20
            reasons.append(f"{trend['trend']}，宜謹慎")
        
        # 量價關係（20%權重）
        if volume_price['relation'] == '價漲量增':
            score += 10
            reasons.append('價漲量增，買盤積極')
        elif volume_price['signal'] == '背離':
            score -= 10
            reasons.append('量價背離，需注意反轉')
        
        # 技術指標（10%權重）
        if technical_signals:
            rsi = technical_signals.get('rsi', {}).get('value', 50)
            if rsi > 70:
                score -= 5
                reasons.append('RSI超買')
            elif rsi < 30:
                score += 5
                reasons.append('RSI超賣')
        
        # 綜合建議
        if score >= 70:
            recommendation = '多頭強勢'
            confidence = '高'
        elif score >= 55:
            recommendation = '偏多持有'
            confidence = '中'
        elif score >= 45:
            recommendation = '中性觀望'
            confidence = '中'
        elif score >= 30:
            recommendation = '偏空減碼'
            confidence = '中'
        else:
            recommendation = '空頭續弱'
            confidence = '高'
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': round(score, 2),
            'reasons': reasons
        }

# 測試函數
if __name__ == '__main__':
    # 生成測試數據
    np.random.seed(42)
    test_prices = pd.Series(np.cumsum(np.random.randn(300)) + 100)
    test_volumes = pd.Series(np.random.randint(1000, 10000, 300))
    
    analyzer = PositionAnalyzer()
    
    # 測試位階分析
    position = analyzer.calculate_position_level(test_prices)
    print("位階分析:", position)
    
    # 測試趨勢分析
    trend = analyzer.analyze_trend(test_prices)
    print("\n趨勢分析:", trend)
    
    # 測試量價關係
    volume_price = analyzer.analyze_volume_price_relation(test_prices, test_volumes)
    print("\n量價關係:", volume_price)
    
    # 綜合判斷
    judgment = analyzer.comprehensive_judgment(position, trend, volume_price)
    print("\n綜合判斷:", judgment)
