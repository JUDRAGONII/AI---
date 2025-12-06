"""
外匯分析器
提供USD/TWD匯率分析與監控
"""
import psycopg2
from datetime import datetime, timedelta

class ForexAnalyzer:
    """外匯分析器 - 專注於USD/TWD"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def get_current_rate(self):
        """獲取當前USD/TWD匯率"""
        # 這裡應該從資料庫或API獲取實際匯率
        # 目前使用模擬數據
        return {
            'rate': 32.15,
            'timestamp': datetime.now().isoformat(),
            'source': 'Mock Data',
            'bid': 32.12,
            'ask': 32.18,
            'spread': 0.06
        }
    
    def analyze_trend(self, days=20):
        """分析匯率趨勢"""
        current_rate = self.get_current_rate()['rate']
        
        # 模擬歷史數據
        # 實際應該從資料庫查詢
        rate_5d_ago = 32.05
        rate_20d_ago = 31.85
        
        # 計算變化
        change_5d = current_rate - rate_5d_ago
        change_20d = current_rate - rate_20d_ago
        
        change_5d_pct = (change_5d / rate_5d_ago) * 100
        change_20d_pct = (change_20d / rate_20d_ago) * 100
        
        # 判斷趨勢
        if change_20d_pct > 0.5:
            trend = '貶值'  # TWD貶值，USD/TWD上升
            trend_eng = 'depreciation'
        elif change_20d_pct < -0.5:
            trend = '升值'  # TWD升值，USD/TWD下降
            trend_eng = 'appreciation'
        else:
            trend = '盤整'
            trend_eng = 'consolidation'
        
        return {
            '當前匯率': current_rate,
            '短期趨勢': {
                '期間': '5日',
                '變化': round(change_5d, 4),
                '變化率': round(change_5d_pct, 2)
            },
            '中期趨勢': {
                '期間': '20日',
                '變化': round(change_20d, 4),
                '變化率': round(change_20d_pct, 2)
            },
            '趨勢判斷': trend,
            'trend_signal': trend_eng,
            '說明': f'新台幣近期呈{trend}態勢'
        }
    
    def get_technical_levels(self):
        """獲取技術面關鍵位"""
        current_rate = self.get_current_rate()['rate']
        
        # 模擬計算支撐壓力
        # 實際應該用技術分析計算
        return {
            '當前價位': current_rate,
            '下檔支撐': {
                '支撐1': 31.80,
                '支撐2': 31.50,
                '說明': '前低與心理關卡'
            },
            '上檔壓力': {
                '壓力1': 32.50,
                '壓力2': 33.00,
                '說明': '前高與整數關卡'
            },
            '區間': {
                '下緣': 31.80,
                '上緣': 32.50,
                '位置': '中性區間'
            }
        }
    
    def analyze_interest_rate_differential(self):
        """分析美台利差"""
        # 這裡應該從資料庫或API獲取實際利率
        us_rate = 5.50  # Fed Funds Rate
        tw_rate = 2.00  # 重貼現率
        
        differential = us_rate - tw_rate
        
        # 判斷利差狀態
        if differential > 3.0:
            status = '擴大'
            impact = '資金傾向流向美元，台幣可能承壓'
        elif differential < 2.0:
            status = '縮小'
            impact = '利差縮小有利台幣'
        else:
            status = '穩定'
            impact = '利差對匯率影響中性'
        
        return {
            '美國聯邦基準利率': us_rate,
            '台灣央行重貼現率': tw_rate,
            '利差': differential,
            '利差狀態': status,
            '影響評估': impact,
            '說明': f'美台利差{differential:.2f}個百分點，{status}'
        }
    
    def analyze_forex_impact_on_stocks(self, market='tw'):
        """分析匯率對股市的影響"""
        trend = self.analyze_trend()
        trend_signal = trend['trend_signal']
        
        if market == 'tw':
            # 台股視角
            if trend_signal == 'depreciation':
                # 台幣貶值
                impact = {
                    '整體影響': '偏正面',
                    '受惠產業': ['電子代工', '紡織', '塑化'],
                    '不利產業': ['航空', '內需零售'],
                    '外資動向': '可能減少買超',
                    '說明': '台幣貶值有利出口導向企業獲利，但可能抑制外資買盤'
                }
            elif trend_signal == 'appreciation':
                # 台幣升值
                impact = {
                    '整體影響': '偏負面',
                    '受惠產業': ['航空', '內需消費'],
                    '不利產業': ['電子代工', '出口製造'],
                    '外資動向': '可能增加買超',
                    '說明': '台幣升值壓抑出口獲利，但吸引外資流入'
                }
            else:
                impact = {
                    '整體影響': '中性',
                    '受惠產業': [],
                    '不利產業': [],
                    '外資動向': '觀望',
                    '說明': '匯率盤整，對股市影響有限'
                }
        else:
            # 美股視角（持有美股的台灣投資人）
            if trend_signal == 'depreciation':
                # 台幣貶值 = 美元升值
                impact = {
                    '整體影響': '正面',
                    '匯兌收益': '美元資產換算台幣增值',
                    '建議': '適合持續持有美股',
                    '說明': '台幣貶值有利美股投資人匯兌收益'
                }
            elif trend_signal == 'appreciation':
                # 台幣升值 = 美元貶值
                impact = {
                    '整體影響': '負面',
                    '匯兌損失': '美元資產換算台幣貶值',
                    '建議': '注意匯兌成本',
                    '說明': '台幣升值侵蝕美股投資收益'
                }
            else:
                impact = {
                    '整體影響': '中性',
                    '匯兌收益': '無明顯影響',
                    '建議': '正常操作',
                    '說明': '匯率平穩，專注標的本身'
                }
        
        return impact
    
    def get_comprehensive_forex_analysis(self, market='tw'):
        """獲取綜合外匯分析"""
        current = self.get_current_rate()
        trend = self.analyze_trend()
        levels = self.get_technical_levels()
        interest = self.analyze_interest_rate_differential()
        impact = self.analyze_forex_impact_on_stocks(market)
        
        # 綜合評估
        favor_score = self._calculate_favor_score(trend, interest, market)
        
        return {
            '當前匯率': current,
            '趨勢分析': trend,
            '技術面關鍵位': levels,
            '美台利差分析': interest,
            '股市影響評估': impact,
            '綜合評估': favor_score,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _calculate_favor_score(self, trend, interest, market):
        """計算匯率環境對投資的有利程度"""
        # 根據市場和趨勢評分
        if market == 'tw':
            # 台股：適度台幣貶值有利
            if trend['trend_signal'] == 'depreciation' and abs(trend['中期趨勢']['變化率']) < 2:
                score = 75
                verdict = '有利'
            elif trend['trend_signal'] == 'appreciation':
                score = 45
                verdict = '不利'
            else:
                score = 60
                verdict = '中性'
        else:
            # 美股（台灣投資人）：台幣貶值有利
            if trend['trend_signal'] == 'depreciation':
                score = 80
                verdict = '有利'
            elif trend['trend_signal'] == 'appreciation':
                score = 40
                verdict = '不利'
            else:
                score = 60
                verdict = '中性'
        
        return {
            '評分': score,
            '判斷': verdict,
            '說明': f'當前匯率環境對{market}市場投資{verdict}'
        }


def get_forex_analysis(db_connection, market='tw'):
    """便利函數：獲取外匯分析"""
    analyzer = ForexAnalyzer(db_connection)
    return analyzer.get_comprehensive_forex_analysis(market)


if __name__ == '__main__':
    # 測試
    print("外匯分析器測試")
    print("=" * 60)
    
    class MockConn:
        pass
    
    analyzer = ForexAnalyzer(MockConn())
    
    # 測試匯率分析
    current = analyzer.get_current_rate()
    print(f"\n當前USD/TWD匯率：{current['rate']}")
    
    trend = analyzer.analyze_trend()
    print(f"趨勢判斷：{trend['趨勢判斷']}")
    print(f"20日變化：{trend['中期趨勢']['變化率']}%")
    
    interest = analyzer.analyze_interest_rate_differential()
    print(f"\n美台利差：{interest['利差']}%")
    print(f"影響：{interest['影響評估']}")
    
    # 測試台股影響
    tw_impact = analyzer.analyze_forex_impact_on_stocks('tw')
    print(f"\n對台股影響：{tw_impact['整體影響']}")
    
    # 測試美股影響
    us_impact = analyzer.analyze_forex_impact_on_stocks('us')
    print(f"對美股投資人影響：{us_impact['整體影響']}")
    
    print("\n✅ 測試完成")
