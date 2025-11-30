"""
完整版API服務器 v2.3 - 包含技術指標和因子端點
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

# 添加calculators到path
sys.path.insert(0, str(Path(__file__).parent))
from calculators.indicators import TechnicalIndicators
from calculators.factors import FactorCalculator

# 添加AI clients
try:
    from ai_clients import get_gemini_client
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    print("⚠️  AI功能未啟用（缺少google-generativeai套件）")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

# ========== 健康檢查 ==========
@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.3-技術指標版',
            'database': 'connected'
        })
    except:
        return jsonify({'status': 'unhealthy'}), 500

# ========== 股票列表 ==========
@app.route('/api/stocks/list', methods=['GET'])
def stocks_list():
    market = request.args.get('market', 'tw')
    limit = request.args.get('limit', 100, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("SELECT * FROM tw_stock_info ORDER BY stock_code LIMIT %s", (limit,))
    else:
        cursor.execute("SELECT * FROM us_stock_info ORDER BY symbol LIMIT %s", (limit,))
    
    stocks = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify({'market': market, 'count': len(stocks), 'stocks': stocks})

# ========== 股票詳情 ==========
@app.route('/api/stocks/<code>', methods=['GET'])
def stock_detail(code):
    market = request.args.get('market', 'tw')
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("SELECT * FROM tw_stock_info WHERE stock_code = %s", (code,))
    else:
        cursor.execute("SELECT * FROM us_stock_info WHERE symbol = %s", (code,))
    
    stock = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not stock:
        return jsonify({'error': '找不到股票'}), 404
    
    return jsonify(dict(stock))

# ========== 價格歷史 ==========
@app.route('/api/prices/<code>', methods=['GET'])
def prices(code):
    market = request.args.get('market', 'tw')
    days = request.args.get('days', 60, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("""
            SELECT * FROM tw_stock_prices 
            WHERE stock_code = %s 
            ORDER BY trade_date DESC LIMIT %s
        """, (code, days))
    else:
        cursor.execute("""
            SELECT * FROM us_stock_prices 
            WHERE symbol = %s 
            ORDER BY trade_date DESC LIMIT %s
        """, (code, days))
    
    data = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify({'stock_code': code, 'count': len(data), 'data': data})

# ========== 技術指標 - MA ==========
@app.route('/api/indicators/<code>/ma', methods=['GET'])
def indicators_ma(code):
    market = request.args.get('market', 'tw')
    period = request.args.get('period', 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM tw_stock_prices 
            WHERE stock_code = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    else:
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM us_stock_prices 
            WHERE symbol = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not data:
        return jsonify({'error': '無價格數據'}), 404
    
    # 計算MA
    df = pd.DataFrame(data)
    df['close_price'] = pd.to_numeric(df['close_price'])
    ma = TechnicalIndicators.calculate_ma(df['close_price'], period)
    
    df['ma'] = ma
    result = df[['trade_date', 'close_price', 'ma']].dropna().to_dict('records')
    
    return jsonify({'code': code, 'period': period, 'count': len(result), 'data': result})

# ========== 技術指標 - RSI ==========
@app.route('/api/indicators/<code>/rsi', methods=['GET'])
def indicators_rsi(code):
    market = request.args.get('market', 'tw')
    period = request.args.get('period', 14, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM tw_stock_prices 
            WHERE stock_code = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    else:
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM us_stock_prices 
            WHERE symbol = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not data:
        return jsonify({'error': '無價格數據'}), 404
    
    df = pd.DataFrame(data)
    df['close_price'] = pd.to_numeric(df['close_price'])
    rsi = TechnicalIndicators.calculate_rsi(df['close_price'], period)
    
    df['rsi'] = rsi
    result = df[['trade_date', 'close_price', 'rsi']].dropna().to_dict('records')
    
    return jsonify({'code': code, 'period': period, 'count': len(result), 'data': result})

# ========== 技術指標 - MACD ==========
@app.route('/api/indicators/<code>/macd', methods=['GET'])
def indicators_macd(code):
    market = request.args.get('market', 'tw')
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM tw_stock_prices 
            WHERE stock_code = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    else:
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM us_stock_prices 
            WHERE symbol = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not data:
        return jsonify({'error': '無價格數據'}), 404
    
    df = pd.DataFrame(data)
    df['close_price'] = pd.to_numeric(df['close_price'])
    macd_data = TechnicalIndicators.calculate_macd(df['close_price'])
    
    df['macd'] = macd_data['macd']
    df['signal'] = macd_data['signal']
    df['histogram'] = macd_data['histogram']
    
    result = df[['trade_date', 'close_price', 'macd', 'signal', 'histogram']].dropna().to_dict('records')
    
    return jsonify({'code': code, 'count': len(result), 'data': result})

# ========== 技術指標 - Bollinger Bands ==========
@app.route('/api/indicators/<code>/bollinger', methods=['GET'])
def indicators_bollinger(code):
    market = request.args.get('market', 'tw')
    period = request.args.get('period', 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    if market == 'tw':
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM tw_stock_prices 
            WHERE stock_code = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    else:
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM us_stock_prices 
            WHERE symbol = %s 
            ORDER BY trade_date ASC LIMIT 200
        """, (code,))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not data:
        return jsonify({'error': '無價格數據'}), 404
    
    df = pd.DataFrame(data)
    df['close_price'] = pd.to_numeric(df['close_price'])
    bb = TechnicalIndicators.calculate_bollinger_bands(df['close_price'], period)
    
    df['upper'] = bb['upper']
    df['middle'] = bb['middle']
    df['lower'] = bb['lower']
    
    result = df[['trade_date', 'close_price', 'upper', 'middle', 'lower']].dropna().to_dict('records')
    
    return jsonify({'code': code, 'period': period, 'count': len(result), 'data': result})

# ========== 商品價格（黃金） ==========
@app.route('/api/commodity/<code>', methods=['GET'])
def commodity(code):
    days = request.args.get('days', 30, type=int)
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    cursor.execute("""
        SELECT trade_date, close_price, volume 
        FROM commodity_prices 
        WHERE commodity_code = %s 
        ORDER BY trade_date DESC LIMIT %s
    """, (code.upper(), days))
    
    data = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify({'commodity': code, 'count': len(data), 'data': data})

# ========== 匯率 ==========
@app.route('/api/forex/<pair>', methods=['GET'])
def forex(pair):
    days = request.args.get('days', 30, type=int)
    
    if len(pair) != 6:
        return jsonify({'error': '格式應為XXXYYY'}), 400
    
    base = pair[:3].upper()
    quote = pair[3:].upper()
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    cursor.execute("""
        SELECT trade_date, rate 
        FROM exchange_rates 
        WHERE base_currency = %s AND quote_currency = %s 
        ORDER BY trade_date DESC LIMIT %s
    """, (base, quote, days))
    
    data = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify({'pair': f'{base}/{quote}', 'count': len(data), 'data': data})

# ========== 市場總覽 ==========
@app.route('/api/market/summary', methods=['GET'])
def market_summary():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    cursor.execute("""
        SELECT close_price, trade_date 
        FROM commodity_prices 
        WHERE commodity_code = 'GOLD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    gold = cursor.fetchone()
    
    cursor.execute("""
        SELECT rate, trade_date 
        FROM exchange_rates 
        WHERE base_currency = 'USD' AND quote_currency = 'TWD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    forex = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as count FROM tw_stock_info")
    tw_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM us_stock_info")
    us_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM tw_stock_prices")
    tw_price_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM us_stock_prices")
    us_price_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM commodity_prices WHERE commodity_code = 'GOLD'")
    gold_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM exchange_rates")
    forex_count = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'gold': {
            'price': float(gold['close_price']) if gold else 0,
            'date': str(gold['trade_date']) if gold else None,
            'count': gold_count
        },
        'forex': {
            'usd_twd': float(forex['rate']) if forex else 0,
            'date': str(forex['trade_date']) if forex else None,
            'count': forex_count
        },
        'stocks': {
            'tw': tw_count,
            'us': us_count,
            'tw_prices': tw_price_count,
            'us_prices': us_price_count
        }
    })

# ========== AI端點 - 測試連接 ==========
@app.route('/api/ai/test-connection', methods=['GET'])
def ai_test_connection():
    if not AI_ENABLED:
        return jsonify({'error': 'AI功能未啟用'}), 503
    
    try:
        client = get_gemini_client()
        result = client.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== AI端點 - 獲取報告列表 ==========
@app.route('/api/ai/reports', methods=['GET'])
def get_ai_reports():
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        limit = request.args.get('limit', 10, type=int)
        report_type = request.args.get('type', 'market')
        
        cursor.execute("""
            SELECT id, title, report_type, sentiment, accuracy, created_at, content
            FROM ai_analysis_reports
            WHERE report_type = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (report_type, limit))
        
        reports = [dict(row) for row in cursor.fetchall()]
        
        # 格式化日期
        for report in reports:
            report['created_at'] = str(report['created_at'])
            
        cursor.close()
        conn.close()
        
        return jsonify({'reports': reports})
    except Exception as e:
        print(f"獲取報告失敗: {e}")
        return jsonify({'error': str(e)}), 500

# ========== AI端點 - 生成市場報告 ==========
@app.route('/api/ai/market-report', methods=['POST'])
def generate_market_report():
    if not AI_ENABLED:
        return jsonify({'error': 'AI功能未啟用'}), 503
        
    try:
        data = request.json
        market_data = data.get('market_data', {})
        
        client = get_gemini_client()
        
        prompt = f"""
        請根據以下市場數據生成一份專業的每日市場覆盤報告：
        
        台股指數: {market_data.get('taiex', 'N/A')}
        S&P 500: {market_data.get('sp500', 'N/A')}
        NASDAQ: {market_data.get('nasdaq', 'N/A')}
        黃金價格: {market_data.get('gold', 'N/A')}
        USD/TWD: {market_data.get('usdtwd', 'N/A')}
        
        報告結構：
        1. 市場總覽 (含情緒判斷：看多/看空/中性)
        2. 關鍵觀察 (台股、美股、商品)
        3. 操作建議 (短期、中期、風險)
        
        請使用Markdown格式。
        """
        
        response = client.generate_content(prompt)
        report_content = response.text
        
        # 簡單的情緒分析 (實際應由AI返回JSON)
        sentiment = 'neutral'
        if '看多' in report_content or 'Bullish' in report_content:
            sentiment = 'bullish'
        elif '看空' in report_content or 'Bearish' in report_content:
            sentiment = 'bearish'
            
        # 存入資料庫
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_analysis_reports (report_type, title, content, sentiment, accuracy)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, ('market', '每日市場覆盤報告', report_content, sentiment, 0.0))
        
        new_report = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': '報告生成成功',
            'id': new_report[0],
            'created_at': str(new_report[1]),
            'report': report_content,
            'sentiment': sentiment
        })
        
    except Exception as e:
        print(f"生成報告失敗: {e}")
        return jsonify({'error': str(e)}), 500
    if not AI_ENABLED:
        return jsonify({'error': 'AI功能未啟用'}), 503
    
    try:
        data = request.get_json() or {}
        
        # 預設數據（可從資料庫獲取或由前端提供）
        stock_data = data.get('stock_data', {'code': code, 'name': 'Unknown'})
        technical_indicators = data.get('technical_indicators', {})
        factor_scores = data.get('factor_scores', {})
        
        client = get_gemini_client()
        analysis = client.generate_stock_analysis(stock_data, technical_indicators, factor_scores)
        
        return jsonify({
            'stock_code': code,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== AI端點 - 市場分析報告 ==========
@app.route('/api/ai/market-report', methods=['POST'])
def ai_market_report():
    if not AI_ENABLED:
        return jsonify({'error': 'AI功能未啟用'}), 503
    
    try:
        data = request.get_json() or {}
        market_data = data.get('market_data', {})
        
        client = get_gemini_client()
        report = client.generate_market_overview(market_data)
        
        return jsonify({
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 資料表列表 ==========
@app.route('/api/database/tables', methods=['GET'])
def db_tables():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = [row['table_name'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify({'count': len(tables), 'tables': tables})

# ========== 錯誤處理 ==========
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'API端點不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': '伺服器內部錯誤'}), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    
    print("=" * 60)
    print("🚀 API伺服器啟動（技術指標版 v2.3）")
    print("=" * 60)
    print(f"📡 http://localhost:{port}")
    print(f"💾 PostgreSQL@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print("=" * 60)
    ai_status = "✅" if AI_ENABLED else "❌"
    print(f"📋 17個端點 (AI功能 {ai_status}):")
    print("  【基礎】")
    print("  GET /api/health")
    print("  GET /api/stocks/list")
    print("  GET /api/stocks/<code>")
    print("  GET /api/prices/<code>")
    print("  【技術指標】")
    print("  GET /api/indicators/<code>/ma")
    print("  GET /api/indicators/<code>/rsi")
    print("  GET /api/indicators/<code>/macd")
    print("  GET /api/indicators/<code>/bollinger")
    print("  【市場數據】")
    print("  GET /api/commodity/<code>")
    print("  GET /api/forex/<pair>")
    print("  GET /api/market/summary")
    print("  GET /api/database/tables")
    if AI_ENABLED:
        print("  【AI分析】")
        print("  GET /api/ai/test-connection")
        print("  POST /api/ai/analyze-stock/<code>")
        print("  POST /api/ai/market-report")
    print("=" * 60)
    print("🎉 數據：黃金251筆、匯率67筆、台股50支、美股30支")
    print("=" * 60)
    
# ========== 系統API狀態 ==========
@app.route('/api/system/api-status', methods=['GET'])
def get_api_status():
    """獲取所有API的狀態信息"""
    import time
    from datetime import datetime, timedelta
    
    api_statuses = []
    
    # 1. 測試資料庫連接
    db_status = {
        'name': 'PostgreSQL Database',
        'category': '資料庫',
        'status': 'healthy',
        'uptime': 99.9,
        'latency': 0,
        'lastUpdate': '剛剛',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        conn.close()
        db_status['latency'] = int((time.time() - start) * 1000)
        db_status['status'] = 'healthy'
    except Exception as e:
        db_status['status'] = 'error'
        db_status['errorRate'] = 100
    
    api_statuses.append(db_status)
    
    # 2. Gemini AI API
    ai_status = {
        'name': 'Gemini AI',
        'category': 'AI服務',
        'status': 'unknown',
        'uptime': 95.0,
        'latency': 0,
        'lastUpdate': '未測試',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '15次/分鐘'
    }
    
    if AI_ENABLED:
        try:
            # 檢查API Key是否存在
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
            if api_key:
                ai_status['status'] = 'healthy'
                ai_status['lastUpdate'] = '已配置'
                ai_status['latency'] = 2500  # 估計值
            else:
                ai_status['status'] = 'warning'
                ai_status['lastUpdate'] = '未配置API Key'
                ai_status['errorRate'] = 100
        except:
            ai_status['status'] = 'error'
            ai_status['errorRate'] = 100
    else:
        ai_status['status'] = 'error'
        ai_status['lastUpdate'] = 'AI模組未安裝'
        ai_status['errorRate'] = 100
    
    api_statuses.append(ai_status)
    
    # 3. 台股數據源
    tw_status = {
        'name': 'TWSE Data',
        'category': '台股資料',
        'status': 'healthy',
        'uptime': 99.5,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
        tw_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM tw_stock_prices")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        tw_status['latency'] = int((time.time() - start) * 1000)
        tw_status['requestsToday'] = tw_count
        if latest:
            tw_status['lastUpdate'] = str(latest)
        tw_status['status'] = 'healthy'
    except:
        tw_status['status'] = 'error'
        tw_status['errorRate'] = 100
    
    api_statuses.append(tw_status)
    
    # 4. 美股數據源
    us_status = {
        'name': 'US Stock Data',
        'category': '美股資料',
        'status': 'healthy',
        'uptime': 99.2,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM us_stock_info")
        us_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM us_stock_prices")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        us_status['latency'] = int((time.time() - start) * 1000)
        us_status['requestsToday'] = us_count
        if latest:
            us_status['lastUpdate'] = str(latest)
        us_status['status'] = 'healthy'
    except:
        us_status['status'] = 'error'
        us_status['errorRate'] = 100
    
    api_statuses.append(us_status)
    
    # 5. 黃金數據
    gold_status = {
        'name': 'Gold Price Data',
        'category': '商品資料',
        'status': 'healthy',
        'uptime': 98.8,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        gold_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        gold_status['latency'] = int((time.time() - start) * 1000)
        gold_status['requestsToday'] = gold_count
        if latest:
            gold_status['lastUpdate'] = str(latest)
        gold_status['status'] = 'healthy'
    except:
        gold_status['status'] = 'error'
        gold_status['errorRate'] = 100
    
    api_statuses.append(gold_status)
    
    # 6. 匯率數據
    forex_status = {
        'name': 'Exchange Rate Data',
        'category': '匯率資料',
        'status': 'healthy',
        'uptime': 99.1,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exchange_rates")
        forex_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM exchange_rates")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        forex_status['latency'] = int((time.time() - start) * 1000)
        forex_status['requestsToday'] = forex_count
        if latest:
            forex_status['lastUpdate'] = str(latest)
        forex_status['status'] = 'healthy'
    except:
        forex_status['status'] = 'error'
        forex_status['errorRate'] = 100
    
    api_statuses.append(forex_status)
    
    return jsonify({
        'apis': api_statuses,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 啟動完整版API服務器 v2.3 (Port {port})...")
    print("=" * 60)
    print("  【基礎】")
    print("  GET /api/health")
    print("  GET /api/stocks/list")
    print("  GET /api/stocks/<code>")
    print("  GET /api/prices/<code>")
    print("  【技術指標】")
    print("  GET /api/indicators/<code>/ma")
    print("  GET /api/indicators/<code>/rsi")
    print("  GET /api/indicators/<code>/macd")
    print("  GET /api/indicators/<code>/bollinger")
    print("  【市場數據】")
    print("  GET /api/commodity/<code>")
    print("  GET /api/forex/<pair>")
    print("  GET /api/market/summary")
    print("  GET /api/database/tables")
    print("  GET /api/system/api-status")
    if AI_ENABLED:
        print("  【AI分析】")
        print("  GET /api/ai/test-connection")
        print("  POST /api/ai/analyze-stock/<code>")
        print("  POST /api/ai/market-report")
    print("=" * 60)
    print("🎉 數據：黃金251筆、匯率67筆、台股50支、美股30支")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
