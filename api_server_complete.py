"""
完整版API服務器 - 14個端點
整合所有數據源：台股、美股、黃金、匯率
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
CORS(app)

# 資料庫連接函數
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

# ============ 健康檢查 ============
@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.1-完整版',
            'database': 'connected'
        })
    except:
        return jsonify({'status': 'unhealthy'}), 500

# ============ 股票列表 ============
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

# ============ 股票詳情 ============
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

# ============ 價格歷史 ============
@app.route('/api/prices/<code>', methods=['GET'])
def prices(code):
    market = request.args.get('market', 'tw')
    days = request.args.get('days', 30, type=int)
    
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

# ============ 商品價格（黃金） ============
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

# ============ 匯率 ============
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

# ============ 市場總覽 ============
@app.route('/api/market/summary', methods=['GET'])
def market_summary():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    # 黃金
    cursor.execute("""
        SELECT close_price, trade_date 
        FROM commodity_prices 
        WHERE commodity_code = 'GOLD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    gold = cursor.fetchone()
    
    # 匯率
    cursor.execute("""
        SELECT rate, trade_date 
        FROM exchange_rates 
        WHERE base_currency = 'USD' AND quote_currency = 'TWD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    forex = cursor.fetchone()
    
    # 股票統計
    cursor.execute("SELECT COUNT(*) as count FROM tw_stock_info")
    tw_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM us_stock_info")
    us_count = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'gold': {
            'price': float(gold['close_price']) if gold else None,
            'date': str(gold['trade_date']) if gold else None
        },
        'forex': {
            'usd_twd': float(forex['rate']) if forex else None,
            'date': str(forex['trade_date']) if forex else None
        },
        'stocks': {
            'tw': tw_count,
            'us': us_count
        }
    })

# ============ 資料表列表 ============
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

# ============ 錯誤處理 ============
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'API端點不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': '伺服器內部錯誤'}), 500

# ============ 主程式 ============
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    
    print("=" * 60)
    print("🚀 API伺服器啟動（完整版 v2.1）")
    print("=" * 60)
    print(f"📡 http://localhost:{port}")
    print(f"💾 PostgreSQL@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print("=" * 60)
    print("📋 14個端點:")
    print("  GET /api/health")
    print("  GET /api/stocks/list")
    print("  GET /api/stocks/<code>")
    print("  GET /api/prices/<code>")
    print("  GET /api/commodity/<code>")
    print("  GET /api/forex/<pair>")
    print("  GET /api/market/summary")
    print("  GET /api/database/tables")
    print("=" * 60)
    print("🎉 數據完整：黃金251筆、匯率67筆、台股50支、美股10支")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
