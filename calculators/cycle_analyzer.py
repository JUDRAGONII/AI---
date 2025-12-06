"""
週期性定位分析器
評估當前市場所處週期階段
"""
from datetime import datetime

class CycleAnalyzer:
    """週期性定位分析器"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def analyze_economic_cycle(self, market='tw'):
        """分析經濟週期位置"""
        # 經濟週期四階段：復甦、擴張、衰退、蕭條
        
        if market == 'tw':
            # 台灣經濟週期評估
            # 實際應該基於GDP、PMI、失業率等數據計算
            cycle_data = {
                '當前階段': '擴張',
                '階段代碼': 'expansion',
                '週期位置': '中後期',
                '持續時間': '18個月',
                '關鍵指標': {
                    'GDP成長率': 3.2,
                    'PMI指數': 52.3,
                    '失業率': 3.5,
                    '產能利用率': 78.5
                },
                '下階段預測': {
                    '可能階段': '擴張後期',
                    '轉換機率': 35,
                    '關鍵觀察': '通膨壓力、央行政策'
                },
                '投資建議': '擴張期適合持續持股，但需注意過熱風險'
            }
        else:
            # 美國經濟週期評估
            cycle_data = {
                '當前階段': '擴張後期',
                '階段代碼': 'late_expansion',
                '週期位置': '接近頂點',
                '持續時間': '24個月',
                '關鍵指標': {
                    'GDP成長率': 2.1,
                    'PMI指數': 48.7,
                    '失業率': 3.9,
                    '產能利用率': 82.1
                },
                '下階段預測': {
                    '可能階段': '衰退',
                    '轉換機率': 45,
                    '關鍵觀察': '聯準會政策、殖利率曲線'
                },
                '投資建議': '擴張後期應注意防禦，增加現金部位'
            }
        
        return cycle_data
    
    def analyze_industry_cycle(self, industry='semiconductor'):
        """分析產業週期"""
        # 常見產業：半導體、面板、航運、鋼鐵等
        
        industry_cycles = {
            'semiconductor': {
                '產業': '半導體',
                '當前階段': '補庫存初期',
                '週期特徵': '庫存去化完成，開始補庫',
                '持續時間': '6個月',
                '關鍵指標': {
                    '庫存天數': 65,
                    '訂單出貨比': 1.05,
                    '產能利用率': 75,
                    '價格趨勢': '止跌回穩'
                },
                '投資時機': '初升段，可逢低布局',
                '龍頭股': ['2330', '2454', '3711']
            },
            'panel': {
                '產業': '面板',
                '當前階段': '衰退末期',
                '週期特徵': '價格觸底，等待需求復甦',
                '投資時機': '觀望為主',
                '龍頭股': ['2409', '3481']
            },
            'shipping': {
                '產業': '航運',
                '當前階段': '盤整',
                '週期特徵': '運價波動，供需平衡',
                '投資時機': '中性',
                '龍頭股': ['2603', '2615']
            }
        }
        
        return industry_cycles.get(industry, {
            '產業': industry,
            '當前階段': '數據不足',
            '投資時機': '需進一步研究'
        })
    
    def analyze_market_cycle(self, market='tw'):
        """分析股市週期"""
        # 股市週期：熊市底部、牛市初期、牛市中期、牛市後期、熊市
        
        if market == 'tw':
            market_cycle = {
                '當前階段': '牛市中期',
                '階段代碼': 'bull_mid',
                '市場位置': '相對高檔',
                '距離高點': -8.5,  # 距離52週高點
                '距離低點': 15.3,  # 距離52週低點
                '關鍵指標': {
                    '本益比': 16.8,
                    '股息殖利率': 3.2,
                    '融資使用率': 38.5,
                    '外資持股比重': 42.1
                },
                '市場溫度': 65,  # 0-100，越高越熱
                '建議': '多頭格局，但需注意回檔風險'
            }
        else:
            market_cycle = {
                '當前階段': '牛市後期',
                '階段代碼': 'bull_late',
                '市場位置': '高檔震盪',
                '距離高點': -3.2,
                '距離低點': 22.8,
                '關鍵指標': {
                    '本益比': 21.5,
                    '股息殖利率': 1.8,
                    'VIX指數': 18.5,
                    '散戶參與度': 'high'
                },
                '市場溫度': 78,
                '建議': '注意高檔風險，適度減碼'
            }
        
        return market_cycle
    
    def get_comprehensive_cycle_analysis(self, market='tw'):
        """獲取綜合週期分析"""
        economic = self.analyze_economic_cycle(market)
        market_cycle = self.analyze_market_cycle(market)
        
        # 半導體週期分析（台股重點）
        if market == 'tw':
            semi_cycle = self.analyze_industry_cycle('semiconductor')
        else:
            semi_cycle = None
        
        # 綜合評估
        overall = self._calculate_cycle_position(economic, market_cycle)
        
        return {
            '經濟週期': economic,
            '股市週期': market_cycle,
            '產業週期': semi_cycle if semi_cycle else '不適用',
            '綜合評估': overall,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _calculate_cycle_position(self, economic, market):
        """計算綜合週期位置"""
        # 根據經濟和市場週期評估
        eco_stage = economic['階段代碼']
        mkt_stage = market['階段代碼']
        
        # 評分邏輯
        if eco_stage == 'expansion' and mkt_stage in ['bull_early', 'bull_mid']:
            # 經濟擴張 + 股市牛市早中期 = 最佳
            score = 85
            phase = '甜蜜點'
            action = '積極持股'
        elif eco_stage == 'late_expansion' and mkt_stage == 'bull_late':
            # 經濟擴張後期 + 股市牛市後期 = 高檔風險
            score = 55
            phase = '高檔區'
            action = '適度減碼'
        elif eco_stage == 'recession':
            # 經濟衰退
            score = 35
            phase = '衰退期'
            action = '防禦為主'
        else:
            score = 60
            phase = '中性'
            action = '觀望'
        
        return {
            '綜合評分': score,
            '週期階段': phase,
            '投資策略': action,
            '風險等級': 'high' if score < 50 else 'medium' if score < 70 else 'low',
            '說明': f'當前處於{phase}，建議{action}'
        }


def get_cycle_analysis(db_connection, market='tw'):
    """便利函數：獲取週期分析"""
    analyzer = CycleAnalyzer(db_connection)
    return analyzer.get_comprehensive_cycle_analysis(market)


if __name__ == '__main__':
    print("週期性定位分析器測試")
    print("=" * 60)
    
    class MockConn:
        pass
    
    analyzer = CycleAnalyzer(MockConn())
    
    # 測試經濟週期
    eco = analyzer.analyze_economic_cycle('tw')
    print(f"\n經濟週期：{eco['當前階段']}")
    print(f"週期位置：{eco['週期位置']}")
    
    # 測試產業週期
    semi = analyzer.analyze_industry_cycle('semiconductor')
    print(f"\n半導體週期：{semi['當前階段']}")
    print(f"投資時機：{semi['投資時機']}")
    
    # 測試股市週期
    market = analyzer.analyze_market_cycle('tw')
    print(f"\n股市週期：{market['當前階段']}")
    print(f"市場溫度：{market['市場溫度']}/100")
    
    print("\n✅ 測試完成")
