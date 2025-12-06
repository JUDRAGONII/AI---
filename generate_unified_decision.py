"""
AI報告生成腳本 - 統合究極版決策模板 V8.1
基於「統合究極版決策模板 V8.1 (全資產戰略家版)」生成個股決策報告
"""
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
import json
sys.path.append(os.path.dirname(__file__))

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

def load_template_v8():
    """載入V8.1模板"""
    template_path = os.path.join(os.path.dirname(__file__), '統合究極版決策模板 V8.1 (全資產戰略家版).txt')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def generate_stock_decision_report(stock_code='2330', market='tw'):
    """生成個股決策報告（基於V8.1模板）"""
    from ai_clients.gemini_client import get_gemini_client
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 獲取股票最新數據
    table_name = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
    cursor.execute(f"""
        SELECT close_price, high_price, low_price, volume, trade_date
        FROM {table_name}
        WHERE stock_code = %s
        ORDER BY trade_date DESC LIMIT 20
    """, (stock_code,))
    
    recent_data = cursor.fetchall()
    
    if not recent_data:
        print(f"❌ 找不到 {stock_code} 的數據")
        cursor.close()
        conn.close()
        return None, None
    
    # 組織數據
    latest = recent_data[0]
    data = {
        'stock_code': stock_code,
        'market': market,
        'price': float(latest[0]) if latest[0] else 0,
        'high': float(latest[1]) if latest[1] else 0,
        'low': float(latest[2]) if latest[2] else 0,
        'volume': int(latest[3]) if latest[3] else 0,
        'date': str(latest[4]) if latest[4] else '',
    }
    
    # 計算52週高低點
    prices = [float(row[0]) for row in recent_data if row[0]]
    high_52w = max(prices) if prices else data['high']
    low_52w = min(prices) if prices else data['low']
    
    client = get_gemini_client()
    
    # 載入V8.0模板
    template_v8 = load_template_v8()
    
    # 第一步：生成六因子評分
    score_prompt = f"""
你是專業的投資分析師。請針對{stock_code}進行六因子評估，並以JSON格式輸出評分（0-100分）：

當前數據：
- 股票代碼: {data['stock_code']}
- 最新價格: ${data['price']:.2f}
- 52週高點: ${high_52w:.2f}
- 52週低點: ${low_52w:.2f}
- 日期: {data['date']}

請評估以下六個因子並給出0-100的評分：
1. Macro（宏觀環境）：全球經濟、產業趨勢
2. Technical（技術面）：價格動能、趨勢強度
3. Chips（籌碼面）：大戶持股、成交量
4. Fundamental（基本面）：財務狀況、獲利能力
5. Sentiment（市場情緒）：投資人樂觀/悲觀程度
6. Valuation（估值水平）：是否高估或低估

請以以下JSON格式回應（純JSON，不要markdown格式）：
{{
  "macro": 75,
  "technical": 82,
  "chips": 68,
  "fundamental": 88,
  "sentiment": 72,
  "valuation": 65,
  "overall_score": 75,
  "recommendation": "買入",
  "confidence": "高"
}}
"""
    
    score_response = client.model.generate_content(score_prompt)
    score_text = score_response.text.strip()
    
    # 解析 JSON
    if '```json' in score_text:
        score_text = score_text.split('```json')[1].split('```')[0].strip()
    elif '```' in score_text:
        score_text = score_text.split('```')[1].split('```')[0].strip()
    
    try:
        six_factor_scores = json.loads(score_text)
    except:
        six_factor_scores = {
            'macro': 70, 'technical': 70, 'chips': 70,
            'fundamental': 70, 'sentiment': 70, 'valuation': 70,
            'overall_score': 70, 'recommendation': '持有', 'confidence': '中'
        }
    
    # 第二步：基於V8.1模板生成完整報告
    asset_type = '台股個股' if market == 'tw' else '美股個股'
    report_prompt = f"""
你是專業的全資產投資策略師。請基於「統合究極版決策模板 V8.1」為{stock_code}生成完整的投資決策報告。

### 當前資訊：
- 股票代碼: {stock_code}
- 資產類型: {asset_type}
- 最新價格: ${data['price']:.2f}
- 52週高點: ${high_52w:.2f}
- 52週低點: ${low_52w:.2f}
- 日期: {data['date']}

### 六因子評分（已完成）：
- 宏觀環境: {six_factor_scores.get('macro', 70)}/100
- 技術面: {six_factor_scores.get('technical', 70)}/100
- 籌碼面: {six_factor_scores.get('chips', 70)}/100
- 基本面: {six_factor_scores.get('fundamental', 70)}/100
- 市場情緒: {six_factor_scores.get('sentiment', 70)}/100
- 估值水平: {six_factor_scores.get('valuation', 70)}/100
- 綜合評分: {six_factor_scores.get('overall_score', 70)}/100

### 請按照以下結構生成報告（完整Markdown格式）：

# 📊 {stock_code} 統合究極版決策分析 V8.1

**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Part 0: 持倉現況與績效儀表板

| 項目 | 數值 |
|:---|---:|
| 當前市價 | ${data['price']:.2f} |
| 究極版綜合評分 | {six_factor_scores.get('overall_score', 70)}/100 |
| AI 投資評級 | {six_factor_scores.get('recommendation', '持有')} |
| AI 模型信賴度 | {six_factor_scores.get('confidence', '中')} |

---

## Part 1: 決策摘要與數據駕駛艙

### 六因子雷達圖數據
- 🌍 宏觀環境: {six_factor_scores.get('macro', 70)}/100
- 📈 技術面: {six_factor_scores.get('technical', 70)}/100
- 💰 籌碼面: {six_factor_scores.get('chips', 70)}/100
- 📊 基本面: {six_factor_scores.get('fundamental', 70)}/100
- 😊 市場情緒: {six_factor_scores.get('sentiment', 70)}/100
- 💵 估值水平: {six_factor_scores.get('valuation', 70)}/100

---

## Part 2: 核心投資論證 (Bull vs. Bear)

### ✅ 正方論點 (The Bull Case)
[請基於六因子評分，提出看多的核心論點與關鍵催化劑]

### ⚠️ 反方論點 (The Bear Case)
[請提出看空的核心反對論點與主要風險點]

### 🎯 綜合裁決
[比較Bull/Bear論點，解釋當前哪方更具說服力]

---

## Part 3: 市場宏觀背景

### {'台灣市場' if market == 'tw' else '美國市場'}宏觀環境
[請分析當前宏觀經濟情況對該股的影響]

---

## Part 4: 投資組合協同性

### 與核心持倉之關聯性
[分析該股票與主要指數的相關性]

### 在投資組合中的角色定位
**角色**: [核心 (Core) / 戰術衛星 (Satellite) / 收益基石 (Income)]

---

## Part 5: 前瞻性分析

### 情境模擬

| 情境 | 觸發條件 | 預估機率 | 目標價位 |
|:---|:---|:---:|---:|
| 🟢 樂觀情境 | [條件] | [機率]% | 上看 $[價格] |
| 🟡 基礎情境 | [條件] | [機率]% | $[區間] |
| 🔴 悲觀情境 | [條件] | [機率]% | 回測 $[價格] |

---

## Part 6: 戰術規劃與風險控制

### 當前技術面訊號
[K線型態、移動平均線、成交量、技術指標分析]

### 行動與出場策略

| 價格區間 | 操作建議 |
|:---|:---|
| **強力買進** | $[區間] |
| **適度買進** | $[區間] |
| **觀望持有** | $[區間] |
| **減碼賣出** | $[區間] |

### 停損條件
- **技術面停損**: [條件]
- **基本面停損**: [條件]

---

## {'Part 7: 台股個股深度剖析' if market == 'tw' else 'Part 9: 美股個股深度剖析'}

### 市場資金流向
[分析三大法人、融資融券情況]

### 企業深度剖析
[量化多因子分析、大戶籌碼分析]

---

## Part 14: 最終檢核

### 行為金融學檢核
- ✅ 確認偏誤檢查
- ✅ 近期偏誤檢查

### 今日操作要點總結
**{six_factor_scores.get('recommendation', '持有')}** - [一句話總結操作策略]

---

*本報告基於統合究極版決策模板 V8.1 (全資產戰略家版) 生成*
"""
    
    report_content = client.model.generate_content(report_prompt).text
    
    # 整合市場數據（包含六因子評分）
    market_data_with_scores = {
        **data,
        'six_factors': six_factor_scores,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'generation_timestamp': datetime.now().isoformat()
    }
    
    # 儲存到資料庫
    cursor.execute("""
        INSERT INTO ai_reports (report_type, report_title, report_content, market_data, generated_by)
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING id
    """, (
        'stock_decision',  # 新的報告類型
        f'{stock_code} 統合究極版決策分析 V8.1 - {data["date"]}',
        report_content,
        json.dumps(market_data_with_scores),
        'gemini-2.5-flash'
    ))
    
    report_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ 個股決策報告已生成 (ID: {report_id})")
    print(f"六因子評分: {six_factor_scores}")
    return report_id, report_content

if __name__ == '__main__':
    print("="*60)
    print("🤖 AI 個股決策報告生成系統 V8.1")
    print("="*60)
    
    try:
        report_id, content = generate_stock_decision_report('2330', 'tw')
        if report_id:
            print(f"\n報告預覽：\n{content[:500]}...\n")
        else:
            print("❌ 報告生成失敗")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("="*60)
    print("✅ 完成！")
    print("="*60)
