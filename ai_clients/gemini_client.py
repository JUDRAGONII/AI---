"""
Gemini AI Client - Google Gemini API 整合
功能：
1. 與 Gemini API 連接
2. 生成股市分析報告
3. AI投資建議生成
4. Token使用追蹤
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional
from datetime import datetime


class GeminiClient:
    """Gemini API 客戶端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini Client
        
        Args:
            api_key: Google AI API金鑰，若未提供則從環境變數讀取
        """
        # 優先使用傳入的 API key，否則從環境變數讀取
        # 支持 GOOGLE_AI_API_KEY 或 GEMINI_API_KEY
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Google AI API key not found. Please set GOOGLE_AI_API_KEY or GEMINI_API_KEY environment variable.")
        
        
        # 配置 API
        genai.configure(api_key=self.api_key)
        
        # 使用 Gemini 2.5 Flash 模型
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 追蹤使用統計
        self.requests_count = 0
        self.tokens_used = 0
    
    def test_connection(self) -> Dict:
        """
        測試 API 連接
        
        Returns:
            Dict: 包含連接狀態的字典
        """
        try:
            response = self.model.generate_content("測試連接，請回覆OK")
            self.requests_count += 1
            return {
                "status": "success",
                "message": "Gemini API 連接成功",
                "response": response.text,
                "model": "gemini-2.5-flash"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"連接失敗: {str(e)}"
            }
    
    def generate_stock_analysis(self, stock_data: Dict, technical_indicators: Dict, 
                                factor_scores: Dict) -> str:
        """
        生成個股深度分析報告
        
        Args:
            stock_data: 股票基本資訊
            technical_indicators: 技術指標數據
            factor_scores: 因子分數
            
        Returns:
            str: AI 生成的分析報告
        """
        prompt = f"""
你是一位專業的量化分析師，請基於以下數據生成詳細的股票分析報告：

## 股票資訊
- 代碼：{stock_data.get('code')}
- 名稱：{stock_data.get('name')}
- 產業：{stock_data.get('industry')}
- 市場：{stock_data.get('market')}

## 技術指標
- RSI(14): {technical_indicators.get('rsi', 'N/A')}
- MACD: {technical_indicators.get('macd', 'N/A')}
- 移動平均線: {technical_indicators.get('ma', 'N/A')}
- 布林通道: {technical_indicators.get('bollinger', 'N/A')}

## 量化因子分數
- 價值因子：{factor_scores.get('value', 'N/A')}
- 品質因子：{factor_scores.get('quality', 'N/A')}
- 動能因子：{factor_scores.get('momentum', 'N/A')}
- 成長因子：{factor_scores.get('growth', 'N/A')}

請生成包含以下內容的分析報告：
1. 技術面分析
2. 基本面評估
3. 風險評估
4. 投資建議（買入/持有/賣出）
5. 關鍵觀察點

報告應專業、客觀、具有可操作性。
"""
        
        try:
            response = self.model.generate_content(prompt)
            self.requests_count += 1
            return response.text
        except Exception as e:
            return f"AI分析生成失敗: {str(e)}"
    
    def generate_market_overview(self, market_data: Dict) -> str:
        """
        生成市場總覽分析報告
        
        Args:
            market_data: 市場數據（指數、匯率、商品等）
            
        Returns:
            str: AI 生成的市場分析
        """
        prompt = f"""
你是一位宏觀市場分析師，請基於以下市場數據生成每日市場覆盤報告：

## 市場數據
- 台股加權指數：{market_data.get('taiex', 'N/A')}
- S&P 500：{market_data.get('sp500', 'N/A')}
- NASDAQ：{market_data.get('nasdaq', 'N/A')}
- VIX 恐慌指數：{market_data.get('vix', 'N/A')}
- 黃金價格：{market_data.get('gold', 'N/A')}
- USD/TWD：{market_data.get('usdtwd', 'N/A')}

請生成包含以下內容的市場分析：
1. 市場整體趨勢
2. 主要驅動因素
3. 風險提示
4. 短期展望
5. 操作建議

報告應簡潔、專業、具有前瞻性。
"""
        
        try:
            response = self.model.generate_content(prompt)
            self.requests_count += 1
            return response.text
        except Exception as e:
            return f"市場分析生成失敗: {str(e)}"
    
    def generate_portfolio_advice(self, portfolio_data: Dict, risk_profile: str = 'moderate') -> str:
        """
        生成投資組合建議
        
        Args:
            portfolio_data: 投資組合數據
            risk_profile: 風險屬性 (conservative/moderate/aggressive)
            
        Returns:
            str: AI 生成的投資建議
        """
        prompt = f"""
你是一位專業的投資顧問，請基於客戶的投資組合生成個人化建議：

## 風險屬性
{risk_profile}

## 投資組合資訊
- 總資產：{portfolio_data.get('total_value', 'N/A')}
- 總成本：{portfolio_data.get('total_cost', 'N/A')}
- 總損益：{portfolio_data.get('total_return', 'N/A')}
- 持股數量：{portfolio_data.get('holdings_count', 'N/A')}

## 資產配置
{portfolio_data.get('allocation', 'N/A')}

請生成包含以下內容的投資建議：
1. 當前配置評估
2. 風險分析
3. 再平衡建議
4. 具體操作建議（買入/賣出）
5. 預期效果

建議應符合客戶的風險屬性，專業且務實。
"""
        
        try:
            response = self.model.generate_content(prompt)
            self.requests_count += 1
            return response.text
        except Exception as e:
            return f"投資建議生成失敗: {str(e)}"
    
    def get_statistics(self) -> Dict:
        """
        獲取使用統計
        
        Returns:
            Dict: API使用統計
        """
        return {
            "requests_count": self.requests_count,
            "tokens_used": self.tokens_used,
            "last_update": datetime.now().isoformat()
        }


# 創建全域實例（單例模式）
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """獲取 Gemini Client 單例"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
