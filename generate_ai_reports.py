"""
AI報告生成腳本 - 建立資料庫表格並生成測試報告
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

def create_reports_table():
    """建立AI報告表格"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_reports (
            id SERIAL PRIMARY KEY,
            report_type VARCHAR(50) NOT NULL,
            report_title VARCHAR(200) NOT NULL,
            report_content TEXT NOT NULL,
            market_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generated_by VARCHAR(50) DEFAULT 'gemini-2.5-flash'
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ ai_reports 表格已建立")

def generate_daily_strategy_report():
    """生成每日戰略報告"""
    from ai_clients.gemini_client import get_gemini_client
    
    # 獲取市場數據
    conn = get_db()
    cursor = conn.cursor()
    
    # 獲取最新市場數據
    cursor.execute("""
        SELECT close_price, trade_date FROM commodity_prices 
        WHERE commodity_code = 'GOLD' ORDER BY trade_date DESC LIMIT 1
    """)
    gold_data = cursor.fetchone()
    
    cursor.execute("""
        SELECT rate, trade_date FROM exchange_rates 
        WHERE base_currency = 'USD' AND quote_currency = 'TWD'
        ORDER BY trade_date DESC LIMIT 1
    """)
    forex_data = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
    tw_stocks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM us_stock_info")
    us_stocks = cursor.fetchone()[0]
    
    market_data = {
        'gold_price': float(gold_data[0]) if gold_data else 0,
        'gold_date': str(gold_data[1]) if gold_data else '',
        'usd_twd': float(forex_data[0]) if forex_data else 0,
        'forex_date': str(forex_data[1]) if forex_data else '',
        'tw_stocks': tw_stocks,
        'us_stocks': us_stocks,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 使用Gemini生成報告
    client = get_gemini_client()
    
    prompt = f"""
你是一位專業的量化投資分析師。請基於以下市場數據生成今日投資戰略報告：

## 市場數據 ({market_data['date']})
- 黃金價格：${market_data['gold_price']:.2f} (更新日期：{market_data['gold_date']})
- USD/TWD匯率：{market_data['usd_twd']:.2f} (更新日期：{market_data['forex_date']})
- 台股追蹤股票：{market_data['tw_stocks']}支
- 美股追蹤股票：{market_data['us_stocks']}支

請生成包含以下內容的每日戰略報告：

# 📊 每日投資戰略報告 - {market_data['date']}

## 1. 市場概況
[分析當前市場環境，包含台股、美股、黃金、匯率]

## 2. 關鍵觀察
[列出3-5個今日重要觀察點]

## 3. 今日操作策略
[提供具體的買入/賣出/觀望建議]

## 4. 風險提示
[列出需要注意的風險因素]

## 5. 明日展望
[對明天市場的預測與建議]

報告應專業、簡潔、可操作性強。
"""
    
    report_content = client.model.generate_content(prompt).text
    
    # 儲存到資料庫
    cursor.execute("""
        INSERT INTO ai_reports (report_type, report_title, report_content, market_data, generated_by)
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING id
    """, (
        'daily_strategy',
        f'每日投資戰略報告 - {market_data["date"]}',
        report_content,
        json.dumps(market_data),
        'gemini-2.5-flash'
    ))
    
    report_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ 每日戰略報告已生成 (ID: {report_id})")
    return report_id, report_content

def generate_0050_decision_report():
    """生成0050決策模板"""
    from ai_clients.gemini_client import get_gemini_client
    import json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 獲取0050數據（使用2330作為代替示例）
    cursor.execute("""
        SELECT close_price, high_price, low_price, volume, trade_date
        FROM tw_stock_prices
        WHERE stock_code = '2330'
        ORDER BY trade_date DESC LIMIT 1
    """)
    stock_data = cursor.fetchone()
    
    data = {
        'code': '0050',
        'price': float(stock_data[0]) if stock_data else 0,
        'high': float(stock_data[1]) if stock_data else 0,
        'low': float(stock_data[2]) if stock_data else 0,
        'volume': int(stock_data[3]) if stock_data else 0,
        'date': str(stock_data[4]) if stock_data else '',
    }
    
    client = get_gemini_client()
    
    prompt = f"""
你是一位專業的ETF投資顧問。請針對元大台灣50 (0050) 生成投資決策報告：

## 0050 當前數據
- 最新價格：${data['price']:.2f}
- 最高價：${data['high']:.2f}
- 最低價：${data['low']:.2f}
- 成交量：{data['volume']:,}
- 日期：{data['date']}

請生成投資決策報告：

# 📈 元大台灣50 (0050) 投資決策

## 1. 當前評估
[分析當前價位是否合理]

## 2. 技術面分析
[價格趨勢、支撐阻力分析]

## 3. 投資建議
- **操作建議**：[買入/持有/賣出]
- **建議價位**：[具體價格區間]
- **停損點**：[風險控制價位]
- **目標價**：[預期目標]

## 4. 資金配置建議
[建議投入資金比例]

## 5. 風險評估
[列出投資風險]

報告應客觀、專業、可執行。
"""
    
    report_content = client.model.generate_content(prompt).text
    
    cursor.execute("""
        INSERT INTO ai_reports (report_type, report_title, report_content, market_data, generated_by)
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING id
    """, (
        '0050_decision',
        f'元大台灣50 (0050) 投資決策 - {data["date"]}',
        report_content,
        json.dumps(data),
        'gemini-2.5-flash'
    ))
    
    report_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ 0050決策報告已生成 (ID: {report_id})")
    return report_id, report_content

def generate_portfolio_strategy_report():
    """生成投資組合策略報告"""
    from ai_clients.gemini_client import get_gemini_client
    import json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 獲取台股前5大持股
    cursor.execute("""
        SELECT stock_code, close_price, trade_date
        FROM tw_stock_prices
        WHERE stock_code IN ('2330', '2317', '2454', '2412', '2308')
        AND trade_date = (SELECT MAX(trade_date) FROM tw_stock_prices)
        ORDER BY stock_code
    """)
    holdings = cursor.fetchall()
    
    portfolio_data = {
        'holdings': [{'code': h[0], 'price': float(h[1]), 'date': str(h[2])} for h in holdings],
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    client = get_gemini_client()
    
    holdings_text = "\n".join([f"- {h['code']}: ${h['price']:.2f}" for h in portfolio_data['holdings']])
    
    prompt = f"""
你是一位專業的投資組合經理。請針對以下投資組合生成策略報告：

## 當前持倉 ({portfolio_data['date']})
{holdings_text}

請生成投資組合策略報告：

# 💼 投資組合策略報告

## 1. 持倉分析
[分析當前持股結構與產業分布]

## 2. 績效評估
[評估投資組合表現]

## 3. 再平衡建議
[是否需要調整持股比例]

## 4. 具體操作建議
- **建議買入**：[股票代碼與理由]
- **建議減碼**：[股票代碼與理由]
- **建議持有**：[股票代碼與理由]

## 5. 資產配置優化
[理想配置比例建議]

## 6. 風險管理
[投資組合風險評估與對策]

報告應全面、專業、可執行。
"""
    
    report_content = client.model.generate_content(prompt).text
    
    cursor.execute("""
        INSERT INTO ai_reports (report_type, report_title, report_content, market_data, generated_by)
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING id
    """, (
        'portfolio_strategy',
        f'投資組合策略報告 - {portfolio_data["date"]}',
        report_content,
        json.dumps(portfolio_data),
        'gemini-2.5-flash'
    ))
    
    report_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ 投資組合策略報告已生成 (ID: {report_id})")
    return report_id, report_content

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 AI報告生成系統")
    print("=" * 60)
    
    # 步驟1：建立表格
    create_reports_table()
    
    # 步驟2：生成三種報告
    print("\n📝 開始生成報告...")
    
    try:
        daily_id, daily_content = generate_daily_strategy_report()
        print(f"\n每日戰略報告預覽：\n{daily_content[:200]}...\n")
    except Exception as e:
        print(f"❌ 每日戰略報告生成失敗: {e}")
    
    try:
        decision_id, decision_content = generate_0050_decision_report()
        print(f"\n0050決策報告預覽：\n{decision_content[:200]}...\n")
    except Exception as e:
        print(f"❌ 0050決策報告生成失敗: {e}")
    
    try:
        portfolio_id, portfolio_content = generate_portfolio_strategy_report()
        print(f"\n投資組合策略報告預覽：\n{portfolio_content[:200]}...\n")
    except Exception as e:
        print(f"❌ 投資組合策略報告生成失敗: {e}")
    
    print("=" * 60)
    print("✅ 報告生成完成！")
    print("=" * 60)
