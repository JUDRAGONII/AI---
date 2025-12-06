"""
宏觀經濟分析器
提供總體經濟環境評估
"""
import psycopg2
from datetime import datetime, timedelta

class MacroAnalyzer:
    """宏觀經濟分析器"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        
    def analyze_tw_economy(self):
        """分析台灣總體經濟"""
        # 這裡應該從資料庫或API獲取實際數據
        # 目前使用模擬數據展示結構
        
        return {
            '景氣對策信號': {
                '燈號': '綠燈',
                '分數': 26,
                '趨勢': '持平',
                '說明': '景氣穩定'
            },
            'CPI年增率': {
                '數值': 2.35,
                '趨勢': '溫和上升',
                '評估': '通膨溫和'
            },
            'GDP成長率': {
                '數值': 3.2,
                '期間': 'Q3 2024',
                '趨勢': '穩定成長'
            },
            '外銷訂單': {
                '年增率': 5.8,
                '趨勢': '持續成長',
                '評估': '出口動能強勁'
            },
            '央行利率': {
                '重貼現率': 2.0,
                '政策傾向': '中性',
                '最新決策': '維持不變'
            },
            '綜合評估': {
                '評分': 75,  # 0-100
                '狀態': '穩健',
                '風險等級': '低'
            }
        }
    
    def analyze_us_economy(self):
        """分析美國總體經濟"""
        return {
            'Core_PCE': {
                '年增率': 2.8,
                '趨勢': '緩步下降',
                '評估': '仍高於目標'
            },
            'CPI': {
                '年增率': 3.2,
                '核心CPI': 4.0,
                '趨勢': '持續降溫'
            },
            'GDP成長率': {
                '數值': 2.1,
                '期間': 'Q3 2024',
                '趨勢': '穩定'
            },
            '非農就業': {
                '新增人數': 150000,
                '失業率': 3.9,
                '評估': '勞動市場穩健'
            },
            '聯準會政策': {
                '聯邦基準利率': 5.5,
                '政策傾向': '鷹派',
                'FOMC最新聲明': '維持高利率更長時間',
                '下次會議': '2024-12-18'
            },
            '綜合評估': {
                '評分': 68,
                '狀態': '放緩中',
                '風險等級': '中'
            }
        }
    
    def analyze_global_macro(self):
        """全球宏觀經濟概況"""
        return {
            '全球成長': {
                '預測': 2.9,
                '機構': 'IMF',
                '趨勢': '溫和成長'
            },
            '地緣政治': {
                '風險等級': '中',
                '主要事件': ['美中關係', '中東局勢'],
                '影響評估': '影響能源與供應鏈'
            },
            '主要央行政策': {
                'Fed': '鷹派',
                'ECB': '中性偏鷹',
                'BOJ': '超寬鬆',
                '分歧程度': '高'
            }
        }
    
    def get_comprehensive_macro_view(self, market='tw'):
        """獲取綜合宏觀視圖"""
        tw_data = self.analyze_tw_economy()
        us_data = self.analyze_us_economy()
        global_data = self.analyze_global_macro()
        
        # 根據市場決定主要關注點
        if market == 'tw':
            primary = tw_data
            secondary = us_data
            focus = '台灣'
        else:
            primary = us_data
            secondary = tw_data
            focus = '美國'
        
        return {
            'focus_market': focus,
            'primary_economy': primary,
            'secondary_economy': secondary,
            'global_context': global_data,
            'analysis_time': datetime.now().isoformat(),
            'overall_sentiment': self._calculate_overall_sentiment(primary, secondary)
        }
    
    def _calculate_overall_sentiment(self, primary, secondary):
        """計算整體經濟情緒"""
        primary_score = primary['綜合評估']['評分']
        secondary_score = secondary['綜合評估']['評分']
        
        # 加權平均（主要市場70%，次要市場30%）
        overall_score = primary_score * 0.7 + secondary_score * 0.3
        
        if overall_score >= 75:
            sentiment = '樂觀'
            signal = 'positive'
        elif overall_score >= 60:
            sentiment = '中性偏樂觀'
            signal = 'neutral_positive'
        elif overall_score >= 50:
            sentiment = '中性'
            signal = 'neutral'
        elif overall_score >= 40:
            sentiment = '中性偏悲觀'
            signal = 'neutral_negative'
        else:
            sentiment = '悲觀'
            signal = 'negative'
        
        return {
            'score': round(overall_score, 1),
            'sentiment': sentiment,
            'signal': signal,
            'interpretation': f'綜合經濟評分{overall_score:.1f}分，整體{sentiment}'
        }


def get_macro_analysis(db_connection, market='tw'):
    """便利函數：獲取宏觀分析"""
    analyzer = MacroAnalyzer(db_connection)
    return analyzer.get_comprehensive_macro_view(market)


if __name__ == '__main__':
    # 測試
    print("宏觀經濟分析器測試")
    print("=" * 60)
    
    # 模擬連接
    class MockConn:
        pass
    
    analyzer = MacroAnalyzer(MockConn())
    
    # 測試台灣經濟
    tw_result = analyzer.analyze_tw_economy()
    print("\n台灣經濟狀況：")
    print(f"景氣燈號：{tw_result['景氣對策信號']['燈號']}")
    print(f"GDP成長率：{tw_result['GDP成長率']['數值']}%")
    print(f"綜合評分：{tw_result['綜合評估']['評分']}/100")
    
    # 測試美國經濟
    us_result = analyzer.analyze_us_economy()
    print("\n美國經濟狀況：")
    print(f"Core PCE：{us_result['Core_PCE']['年增率']}%")
    print(f"聯準會政策：{us_result['聯準會政策']['政策傾向']}")
    print(f"綜合評分：{us_result['綜合評估']['評分']}/100")
    
    print("\n✅ 測試完成")
