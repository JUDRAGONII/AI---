"""
AI 報告生成器

基於 Gemini 生成投資分析報告
"""
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.gemini_client import GeminiClient
from config.settings import DATABASE_CONFIG
import psycopg2
from loguru import logger


class DailyReportGenerator:
    """每日戰略投資分析報告生成器"""
    
    def __init__(self):
        self.ai_client = GeminiClient()
        self.conn = psycopg2.connect(**DATABASE_CONFIG)
    
    def generate_daily_report(
        self,
        target_date: Optional[str] = None
    ) -> str:
        """
        生成每日戰略投資分析報告
        
        Args:
            target_date: 目標日期（預設今天）
        
        Returns:
            Markdown 格式的報告
        """
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"生成每日戰略報告：{target_date}")
        
        # 1. 收集市場數據
        market_data = self._collect_market_data(target_date)
        
        # 2. 收集宏觀數據
        macro_data = self._collect_macro_data()
        
        # 3. 收集情緒指標
        sentiment_data = self._collect_sentiment_data(target_date)
        
        # 4. 構建 Prompt
        prompt = self._build_daily_report_prompt(
            market_data,
            macro_data,
            sentiment_data,
            target_date
        )
        
        # 5. 生成報告
        report = self.ai_client.generate_text(prompt, temperature=0.7)
        
        # 6. 儲存到資料庫
        self._save_report(report, 'daily_strategy', target_date)
        
        logger.success(f"每日戰略報告生成完成：{target_date}")
        
        return report
    
    def _collect_market_data(self, date: str) -> Dict:
        """收集市場數據"""
        cursor = self.conn.cursor()
        
        data = {}
        
        try:
            # 台股加權指數變化
            cursor.execute("""
                SELECT close_price, volume
                FROM tw_stock_prices
                WHERE stock_code = '0000' AND trade_date = %s
            """, (date,))
            taiex = cursor.fetchone()
            if taiex:
                data['taiex_close'] = taiex[0]
                data['taiex_volume'] = taiex[1]
            
            # VIX（波動率指數）
            # 實際應從資料庫獲取
            data['vix'] = 15.5
            
            # BTC 價格
            # 實際應從資料庫獲取
            data['btc_usd'] = 95000
            
        except Exception as e:
            logger.error(f"收集市場數據失敗：{e}")
        finally:
            cursor.close()
        
        return data
    
    def _collect_macro_data(self) -> Dict:
        """收集宏觀經濟數據"""
        cursor = self.conn.cursor()
        
        data = {}
        
        try:
            # 最新 GDP, CPI, 失業率等
            cursor.execute("""
                SELECT indicator_type, value, release_date
                FROM macro_indicators
                WHERE indicator_type IN ('GDP', 'CPI', 'UNEMPLOYMENT')
                ORDER BY release_date DESC
                LIMIT 3
            """)
            
            for row in cursor.fetchall():
                data[row[0].lower()] = {
                    'value': row[1],
                    'date': row[2]
                }
            
        except Exception as e:
            logger.error(f"收集宏觀數據失敗：{e}")
        finally:
            cursor.close()
        
        return data
    
    def _collect_sentiment_data(self, date: str) -> Dict:
        """收集情緒資料"""
        # 實際應從新聞、社群媒體等獲取
        return {
            'fear_greed_index': 65,  # 0-100
            'news_sentiment': 'neutral',
            'social_sentiment': 'positive'
        }
    
    def _build_daily_report_prompt(
        self,
        market: Dict,
        macro: Dict,
        sentiment: Dict,
        date: str
    ) -> str:
        """構建每日報告Prompt"""
        
        prompt = f"""
你是一位專業的投資策略分析師，請根據以下資料生成 {date} 的每日戰略投資分析報告。

=== 市場數據 ===
- 台股加權指數：{market.get('taiex_close', 'N/A')}
- 成交量：{market.get('taiex_volume', 'N/A')}
- VIX 指數：{market.get('vix', 'N/A')}
- BTC/USD：{market.get('btc_usd', 'N/A')}

=== 宏觀經濟 ===
{self._format_macro_data(macro)}

=== 市場情緒 ===
- 恐懼貪婪指數：{sentiment.get('fear_greed_index', 'N/A')}
- 新聞情緒：{sentiment.get('news_sentiment', 'N/A')}
- 社群情緒：{sentiment.get('social_sentiment', 'N/A')}

=== 報告要求 ===
請以 Markdown 格式撰寫報告，包含以下章節：

# {date} 每日戰略投資分析報告

## 一、市場覆盤
分析當日台股、美股、加密貨幣的表現與關鍵事件

## 二、宏觀環境解讀
基於經濟數據，分析當前經濟週期階段與趨勢

## 三、情緒分析
解讀市場情緒指標，判斷市場氛圍

## 四、AI 核心觀點
提供 3-5 個具體的投資策略建議，包含：
1. 資產配置建議（股/債/現金比例）
2. sector 偏好（哪些產業值得關注）
3. 風險警示

## 五、操作建議
明確的短期戰術指引（未來 1-2 週）

---
請用專業但易懂的語言撰寫，避免模稜兩可的描述，給出明確的方向。
"""
        
        return prompt
    
    def _format_macro_data(self, macro: Dict) -> str:
        """格式化宏觀數據"""
        if not macro:
            return "無宏觀數據"
        
        lines = []
        for key, value in macro.items():
            if isinstance(value, dict):
                lines.append(f"- {key.upper()}: {value.get('value', 'N/A')} ({value.get('date', 'N/A')})")
            else:
                lines.append(f"- {key.upper()}: {value}")
        
        return "\n".join(lines)
    
    def _save_report(
        self,
        content: str,
        report_type: str,
        date: str
    ):
        """儲存報告到資料庫"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                INSERT INTO ai_reports (report_type, report_date, content, created_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (report_type, report_date)
                DO UPDATE SET content = EXCLUDED.content, updated_at = NOW()
            """
            
            cursor.execute(query, (report_type, date, content))
            self.conn.commit()
            
            logger.success(f"報告已儲存：{report_type} @ {date}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"儲存報告失敗：{e}")
        finally:
            cursor.close()
    
    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()


class DecisionTemplateGenerator:
    """統合究極版決策模板生成器"""
    
    def __init__(self):
        self.ai_client = GeminiClient()
        self.conn = psycopg2.connect(**DATABASE_CONFIG)
    
    def generate_decision_template(
        self,
        stock_code: str,
        market: str = 'tw'
    ) -> str:
        """
        生成統合究極版決策模板
        
        根據規格書 Part 1-6 完整生成
        
        Args:
            stock_code: 股票代碼
            market: 市場
        
        Returns:
            完整決策模板 (Markdown)
        """
        logger.info(f"生成決策模板：{stock_code}")
        
        # 1. 收集六因子數據
        factor_data = self._get_factor_scores(stock_code, market)
        
        # 2. 收集財務數據
        financial_data = self._get_financial_data(stock_code, market)
        
        # 3. 收集籌碼數據（TDCC）
        chip_data = self._get_shareholder_data(stock_code)
        
        # 4. 收集新聞與輿情
        sentiment_data = self._get_sentiment_data(stock_code)
        
        # 5. 構建 Prompt
        prompt = self._build_decision_template_prompt(
            stock_code,
            factor_data,
            financial_data,
            chip_data,
            sentiment_data
        )
        
        # 6. 生成模板
        template = self.ai_client.generate_text(prompt, temperature=0.6, max_tokens=8000)
        
        # 7. 儲存
        self._save_template(stock_code, template)
        
        logger.success(f"決策模板生成完成：{stock_code}")
        
        return template
    
    def _get_factor_scores(self, stock_code: str, market: str) -> Dict:
        """獲取因子分數"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT value_score, quality_score, momentum_score,
                       size_score, volatility_score, growth_score, total_score
                FROM quant_scores
                WHERE security_id = (SELECT id FROM securities_master WHERE ticker = %s)
                ORDER BY calculation_date DESC
                LIMIT 1
            """
            
            cursor.execute(query, (stock_code,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'value': row[0],
                    'quality': row[1],
                    'momentum': row[2],
                    'size': row[3],
                    'volatility': row[4],
                    'growth': row[5],
                    'total': row[6]
                }
        except Exception as e:
            logger.error(f"獲取因子分數失敗：{e}")
        finally:
            cursor.close()
        
        return {}
    
    def _get_financial_data(self, stock_code: str, market: str) -> Dict:
        """獲取財務數據"""
        # 簡化版本
        return {
            'pe': 15.5,
            'pb': 2.3,
            'roe': 18.2,
            'revenue_growth': 12.5
        }
    
    def _get_shareholder_data(self, stock_code: str) -> Dict:
        """獲取股權分散數據（TDCC）"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT data_date, total_shareholders, 
                       large_holders_percentage, synchronization_index,
                       smart_money_flow
                FROM shareholder_dispersion
                WHERE stock_code = %s
                ORDER BY data_date DESC
                LIMIT 1
            """
            
            cursor.execute(query, (stock_code,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'date': row[0],
                    'total_shareholders': row[1],
                    'large_holders_pct': row[2],
                    'sync_index': row[3],
                    'money_flow': row[4]
                }
        except Exception as e:
            logger.error(f"獲取籌碼數據失敗：{e}")
        finally:
            cursor.close()
        
        return {}
    
    def _get_sentiment_data(self, stock_code: str) -> Dict:
        """獲取情緒資料"""
        # 實際應從新聞、PTT等獲取
        return {
            'news_sentiment': 'positive',
            'social_mentions': 150,
            'sentiment_score': 0.72
        }
    
    def _build_decision_template_prompt(
        self,
        stock_code: str,
        factors: Dict,
        financials: Dict,
        chips: Dict,
        sentiment: Dict
    ) -> str:
        """構建決策模板Prompt"""
        
        prompt = f"""
你是一位資深投資分析師，請為股票 {stock_code} 生成完整的「統合究極版決策模板」。

=== 六大因子分數 ===
- 價值 (Value): {factors.get('value', 'N/A')}/100
- 品質 (Quality): {factors.get('quality', 'N/A')}/100
- 動能 (Momentum): {factors.get('momentum', 'N/A')}/100
- 規模 (Size): {factors.get('size', 'N/A')}/100
- 波動率 (Volatility): {factors.get('volatility', 'N/A')}/100
- 成長 (Growth): {factors.get('growth', 'N/A')}/100
- **總分**: {factors.get('total', 'N/A')}/100

=== 財務指標 ===
- 本益比 (P/E): {financials.get('pe', 'N/A')}
- 股價淨值比 (P/B): {financials.get('pb', 'N/A')}
- ROE: {financials.get('roe', 'N/A')}%
- 營收成長率: {financials.get('revenue_growth', 'N/A')}%

=== 籌碼分析（TDCC）===
- 總股東數: {chips.get('total_shareholders', 'N/A')}
- 大戶比例: {chips.get('large_holders_pct', 'N/A')}%
- 同步率指標: {chips.get('sync_index', 'N/A')}
- 資金流向: {chips.get('money_flow', 'N/A')}

=== 市場情緒 ===
- 新聞情緒: {sentiment.get('news_sentiment', 'N/A')}
- 社群討論度: {sentiment.get('social_mentions', 'N/A')}
- 情緒分數: {sentiment.get('sentiment_score', 'N/A')}

=== 報告要求 ===
請以 Markdown 格式撰寫完整的決策模板，包含：

# {stock_code} 統合究極版決策模板

## Part 1: 數據駕駛艙
用文字描述六大因子雷達圖的特徵，說明這支股票的因子 DNA

## Part 2: 核心投資論證
### 2.1 Bull Case（看多論證）
至少 3 個具體理由

### 2.2 Bear Case（看空論證）
至少 3 個風險因素

## Part 3: 宏觀背景
分析當前宏觀環境對該股的影響

## Part 4: 企業深度剖析
### 4.Z 動態六因子診斷
詳細解讀每個因子的強弱

### 4.Y 籌碼分析
基於 TDCC 數據，分析大戶動向與同步率

### 4.W 機構持倉
（若有 13F 資料，分析機構持倉）

### 4.X 散戶輿情
基於社群與新聞情緒分析

## Part 5: 前瞻性分析與戰術規劃
- 未來 3 個月展望
- 關鍵催化劑
- 買入/賣出條件

## Part 6: 最終檢核
- 投資建議：買入/持有/賣出
- 目標價
- 停損點
- 持有週期建議

---
請用專業、客觀的語言，提供可執行的建議。
"""
        
        return prompt
    
    def _save_template(self, stock_code: str, content: str):
        """儲存模板"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                INSERT INTO ai_reports (
                    report_type, security_id, content, created_at
                )
                VALUES (
                    'decision_template',
                    (SELECT id FROM securities_master WHERE ticker = %s),
                    %s,
                    NOW()
                )
            """
            
            cursor.execute(query, (stock_code, content))
            self.conn.commit()
            
            logger.success(f"決策模板已儲存：{stock_code}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"儲存模板失敗：{e}")
        finally:
            cursor.close()
    
    def close(self):
        if self.conn:
            self.conn.close()


# 測試
if __name__ == '__main__':
    # 測試每日報告
    daily_gen = DailyReportGenerator()
    try:
        report = daily_gen.generate_daily_report()
        print("=== 每日戰略報告 ===")
        print(report[:500])  # 前 500 字
    finally:
        daily_gen.close()
    
    # 測試決策模板
    # template_gen = DecisionTemplateGenerator()
    # try:
    #     template = template_gen.generate_decision_template('2330', 'tw')
    #     print("\n=== 決策模板 ===")
    #     print(template[:500])
    # finally:
    #     template_gen.close()
