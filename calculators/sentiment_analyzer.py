"""
市場情緒分析器
整合VIX、Put/Call比率等指標評估市場恐慌與貪婪程度
"""
from datetime import datetime

class SentimentAnalyzer:
    """市場情緒分析器"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def analyze_vix_fear_gauge(self):
        """分析VIX恐慌指數"""
        # 實際應該從資料庫或API獲取
        vix_value = 15.8
        
        # VIX解讀標準
        if vix_value < 12:
            level = '極度樂觀'
            sentiment = 'extreme_greed'
            color = 'red'  # 反向指標，極度樂觀可能是頂部
            warning = '市場過度自滿，注意反轉風險'
        elif vix_value < 17:
            level = '低波動'
            sentiment = 'greed'
            color = 'yellow'
            warning = '情緒偏樂觀，保持警覺'
        elif vix_value < 25:
            level = '正常'
            sentiment = 'neutral'
            color = 'green'
            warning = '波動正常範圍'
        elif vix_value < 35:
            level = '恐慌'
            sentiment = 'fear'
            color = 'orange'
            warning = '市場恐慌，可能是買點'
        else:
            level = '極度恐慌'
            sentiment = 'extreme_fear'
            color = 'dark_red'
            warning = '恐慌性拋售，歷史買點'
        
        return {
            'VIX數值': vix_value,
            '情緒等級': level,
            '情緒代碼': sentiment,
            '信號燈': color,
            '解讀': warning,
            '投資建議': self._vix_trading_signal(sentiment)
        }
    
    def analyze_put_call_ratio(self):
        """分析Put/Call比率"""
        # 實際應該從資料庫獲取
        ratio = 0.85
        
        # Put/Call比率解讀
        if ratio > 1.2:
            level = '極度看空'
            signal = 'extreme_bearish'
            action = '反向買點'
        elif ratio > 1.0:
            level = '偏空'
            signal = 'bearish'
            action = '謹慎樂觀'
        elif ratio > 0.7:
            level = '中性'
            signal = 'neutral'
            action = '正常交易'
        elif ratio > 0.5:
            level = '偏多'
            signal = 'bullish'
            action = '注意過熱'
        else:
            level = '極度看多'
            signal = 'extreme_bullish'
            action = '反向賣點'
        
        return {
            'Put/Call比率': ratio,
            '市場看法': level,
            '信號': signal,
            '操作建議': action,
            '說明': f'比率{ratio}，市場{level}'
        }
    
    def analyze_margin_debt(self, market='tw'):
        """分析融資餘額（市場槓桿程度）"""
        # 實際應該從資料庫計算
        if market == 'tw':
            margin_total = 185000  # 億元
            margin_pct = 38.5  # 使用率
            
            if margin_pct > 45:
                level = '過熱'
                risk = 'high'
                warning = '融資過高，回檔風險大'
            elif margin_pct > 35:
                level = '偏高'
                risk = 'medium'
                warning = '融資水位偏高，注意風險'
            elif margin_pct > 25:
                level = '正常'
                risk = 'low'
                warning = '融資水位正常'
            else:
                level = '偏低'
                risk = 'very_low'
                warning = '融資水位低，市場觀望'
            
            return {
                '融資餘額': margin_total,
                '使用率': margin_pct,
                '水位評估': level,
                '風險等級': risk,
                '警示': warning
            }
        else:
            # 美股用margin debt
            return {
                '保證金餘額': 'N/A',
                '說明': '美股數據待整合'
            }
    
    def analyze_retail_sentiment(self):
        """分析散戶情緒"""
        # 實際應該爬取PTT、社群媒體數據
        # 這裡使用模擬數據
        
        return {
            '散戶參與度': '高',
            '熱門話題': ['AI', '半導體', '電動車'],
            '情緒極性': {
                '正面': 65,
                '中性': 25,
                '負面': 10
            },
            '整體情緒': '偏樂觀',
            '警示': '散戶過度樂觀通常是反向指標'
        }
    
    def calculate_fear_greed_index(self, market='tw'):
        """計算恐懼與貪婪指數（0-100）"""
        # 綜合多個指標
        vix = self.analyze_vix_fear_gauge()
        put_call = self.analyze_put_call_ratio()
        margin = self.analyze_margin_debt(market)
        
        # 計算綜合分數
        # VIX低 = 貪婪，VIX高 = 恐懼
        vix_score = max(0, 100 - (vix['VIX數值'] * 3))
        
        # Put/Call低 = 貪婪，Put/Call高 = 恐懼
        pc_score = (1 - min(put_call['Put/Call比率'], 2) / 2) * 100
        
        # 融資高 = 貪婪，融資低 = 恐懼
        margin_score = margin['使用率'] * 2
        
        # 加權平均
        overall_score = (vix_score * 0.4 + pc_score * 0.3 + margin_score * 0.3)
        
        # 判斷等級
        if overall_score >= 75:
            level = '極度貪婪'
            signal = 'extreme_greed'
            action = '謹慎！可能是頂部'
        elif overall_score >= 60:
            level = '貪婪'
            signal = 'greed'
            action = '注意回檔風險'
        elif overall_score >= 45:
            level = '中性偏貪婪'
            signal = 'neutral_greed'
            action = '正常持股'
        elif overall_score >= 30:
            level = '中性偏恐懼'
            signal = 'neutral_fear'
            action = '可逢低加碼'
        elif overall_score >= 15:
            level = '恐懼'
            signal = 'fear'
            action = '分批買進時機'
        else:
            level = '極度恐懼'
            signal = 'extreme_fear'
            action = '歷史買點！'
        
        return {
            '指數': round(overall_score, 1),
            '等級': level,
            '信號': signal,
            '建議': action,
            '組成': {
                'VIX貢獻': round(vix_score, 1),
                'Put/Call貢獻': round(pc_score, 1),
                '融資貢獻': round(margin_score, 1)
            }
        }
    
    def get_comprehensive_sentiment_analysis(self, market='tw'):
        """獲取綜合情緒分析"""
        vix = self.analyze_vix_fear_gauge()
        put_call = self.analyze_put_call_ratio()
        margin = self.analyze_margin_debt(market)
        retail = self.analyze_retail_sentiment()
        fear_greed = self.calculate_fear_greed_index(market)
        
        return {
            'VIX恐慌指數': vix,
            'Put/Call比率': put_call,
            '融資餘額': margin,
            '散戶情緒': retail,
            '恐懼貪婪指數': fear_greed,
            '綜合建議': self._generate_sentiment_recommendation(fear_greed),
            'analysis_time': datetime.now().isoformat()
        }
    
    def _vix_trading_signal(self, sentiment):
        """VIX交易信號"""
        signals = {
            'extreme_greed': '減碼訊號',
            'greed': '獲利了結',
            'neutral': '正常持有',
            'fear': '逢低加碼',
            'extreme_fear': '積極買進'
        }
        return signals.get(sentiment, '觀望')
    
    def _generate_sentiment_recommendation(self, fear_greed):
        """根據恐懼貪婪指數生成建議"""
        score = fear_greed['指數']
        signal = fear_greed['信號']
        
        if signal in ['extreme_greed', 'greed']:
            return {
                '操作方向': '減碼',
                '倉位建議': '降至50-60%',
                '理由': '市場情緒過熱，注意回檔風險',
                '風險等級': '高'
            }
        elif signal in ['extreme_fear', 'fear']:
            return {
                '操作方向': '加碼',
                '倉位建議': '提升至70-80%',
                '理由': '市場恐慌，歷史買點機會',
                '風險等級': '低'
            }
        else:
            return {
                '操作方向': '持有',
                '倉位建議': '維持60-70%',
                '理由': '市場情緒中性，正常操作',
                '風險等級': '中'
            }


def get_sentiment_analysis(db_connection, market='tw'):
    """便利函數：獲取情緒分析"""
    analyzer = SentimentAnalyzer(db_connection)
    return analyzer.get_comprehensive_sentiment_analysis(market)


if __name__ == '__main__':
    print("市場情緒分析器測試")
    print("=" * 60)
    
    class MockConn:
        pass
    
    analyzer = SentimentAnalyzer(MockConn())
    
    vix = analyzer.analyze_vix_fear_gauge()
    print(f"\nVIX: {vix['VIX數值']}")
    print(f"情緒: {vix['情緒等級']}")
    print(f"建議: {vix['投資建議']}")
    
    fear_greed = analyzer.calculate_fear_greed_index('tw')
    print(f"\n恐懼貪婪指數: {fear_greed['指數']}/100")
    print(f"等級: {fear_greed['等級']}")
    print(f"建議: {fear_greed['建議']}")
    
    print("\n✅ 測試完成")
