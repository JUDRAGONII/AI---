"""
籌碼分析計算器 - Institutional Analyzer
分析三大法人（外資、投信、自營商）買賣超與持股變化
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class InstitutionalAnalyzer:
    """三大法人籌碼分析器"""
    
    @staticmethod
    def analyze_daily_trades(trades_df: pd.DataFrame, days: int = 20) -> Dict:
        """
        分析近期三大法人交易狀況
        
        Args:
            trades_df: DataFrame包含columns: trade_date, foreign_buy, foreign_sell,
                       trust_buy, trust_sell, dealer_buy, dealer_sell
            days: 分析天數
            
        Returns:
            {
                'foreign': {...},
                'trust': {...},
                'dealer': {...},
                'summary': {...}
            }
        """
        if len(trades_df) < days:
            days = len(trades_df)
        
        recent_trades = trades_df.tail(days)
        
        # 計算買賣超
        foreign_net = (recent_trades['foreign_buy'] - recent_trades['foreign_sell']).sum()
        trust_net = (recent_trades['trust_buy'] - recent_trades['trust_sell']).sum()
        dealer_net = (recent_trades['dealer_buy'] - recent_trades['dealer_sell']).sum()
        
        # 計算連續買賣超天數
        foreign_days = InstitutionalAnalyzer._count_consecutive_days(
            recent_trades['foreign_buy'] - recent_trades['foreign_sell']
        )
        trust_days = InstitutionalAnalyzer._count_consecutive_days(
            recent_trades['trust_buy'] - recent_trades['trust_sell']
        )
        dealer_days = InstitutionalAnalyzer._count_consecutive_days(
            recent_trades['dealer_buy'] - recent_trades['dealer_sell']
        )
        
        # 判斷多空態勢
        total_net = foreign_net + trust_net + dealer_net
        
        analysis = {
            'foreign': {
                'net_shares': int(foreign_net),
                'net_value': foreign_net * recent_trades['close_price'].iloc[-1] if 'close_price' in recent_trades.columns else 0,
                'consecutive_days': foreign_days,
                'trend': '買超' if foreign_net > 0 else '賣超' if foreign_net < 0 else '中性'
            },
            'trust': {
                'net_shares': int(trust_net),
                'net_value': trust_net * recent_trades['close_price'].iloc[-1] if 'close_price' in recent_trades.columns else 0,
                'consecutive_days': trust_days,
                'trend': '買超' if trust_net > 0 else '賣超' if trust_net < 0 else '中性'
            },
            'dealer': {
                'net_shares': int(dealer_net),
                'net_value': dealer_net * recent_trades['close_price'].iloc[-1] if 'close_price' in recent_trades.columns else 0,
                'consecutive_days': dealer_days,
                'trend': '買超' if dealer_net > 0 else '賣超' if dealer_net < 0 else '中性'
            },
            'summary': {
                'total_net_shares': int(total_net),
                'dominant_force': InstitutionalAnalyzer._get_dominant_force(foreign_net, trust_net, dealer_net),
                'overall_trend': '多頭' if total_net > 0 else '空頭' if total_net < 0 else '中性',
                'signal_strength': min(abs(total_net) / 1000, 100)  # 簡化強度計算
            }
        }
        
        return analysis
    
    @staticmethod
    def _count_consecutive_days(net_series: pd.Series) -> int:
        """計算連續買超/賣超天數"""
        if len(net_series) == 0:
            return 0
        
        latest_value = net_series.iloc[-1]
        if latest_value == 0:
            return 0
        
        is_positive = latest_value > 0
        count = 0
        
        for value in reversed(net_series.values):
            if (is_positive and value > 0) or (not is_positive and value < 0):
                count += 1
            else:
                break
        
        return count if is_positive else -count
    
    @staticmethod
    def _get_dominant_force(foreign: float, trust: float, dealer: float) -> str:
        """判斷主導力量"""
        forces = {
            '外資': abs(foreign),
            '投信': abs(trust),
            '自營商': abs(dealer)
        }
        
        dominant = max(forces, key=forces.get)
        
        if forces[dominant] == 0:
            return '無明顯主力'
        
        return dominant
    
    @staticmethod
    def calculate_holding_changes(holdings_df: pd.DataFrame) -> Dict:
        """
        計算持股變化趨勢
        
        Args:
            holdings_df: DataFrame包含columns: trade_date, foreign_holding, 
                        trust_holding, dealer_holding, total_shares
                        
        Returns:
            持股變化分析結果
        """
        if len(holdings_df) < 2:
            return {'error': '數據不足'}
        
        recent = holdings_df.iloc[-1]
        previous = holdings_df.iloc[-20] if len(holdings_df) >= 20 else holdings_df.iloc[0]
        
        foreign_change = (recent['foreign_holding'] - previous['foreign_holding']) / previous['total_shares'] * 100
        trust_change = (recent['trust_holding'] - previous['trust_holding']) / previous['total_shares'] * 100
        dealer_change = (recent['dealer_holding'] - previous['dealer_holding']) / previous['total_shares'] * 100
        
        return {
            'foreign_holding_pct': round(recent['foreign_holding'] / recent['total_shares'] * 100, 2),
            'trust_holding_pct': round(recent['trust_holding'] / recent['total_shares'] * 100, 2),
            'dealer_holding_pct': round(recent['dealer_holding'] / recent['total_shares'] * 100, 2),
            'foreign_change_pct': round(foreign_change, 2),
            'trust_change_pct': round(trust_change, 2),
            'dealer_change_pct': round(dealer_change, 2),
            'trend': '增持' if (foreign_change + trust_change) > 0 else '減持'
        }

# 測試函數
if __name__ == '__main__':
    # 生成測試數據
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    test_data = pd.DataFrame({
        'trade_date': dates,
        'foreign_buy': np.random.randint(1000, 5000, 30),
        'foreign_sell': np.random.randint(1000, 5000, 30),
        'trust_buy': np.random.randint(500, 2000, 30),
        'trust_sell': np.random.randint(500, 2000, 30),
        'dealer_buy': np.random.randint(200, 1000, 30),
        'dealer_sell': np.random.randint(200, 1000, 30),
        'close_price': 580.0
    })
    
    analyzer = InstitutionalAnalyzer()
    result = analyzer.analyze_daily_trades(test_data, days=20)
    
    print("三大法人籌碼分析:")
    print(f"外資: {result['foreign']}")
    print(f"投信: {result['trust']}")
    print(f"自營商: {result['dealer']}")
    print(f"綜合: {result['summary']}")
