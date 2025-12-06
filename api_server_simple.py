"""
簡化 API Server - 繞過 api_server_v3.py 的縮排錯誤
直接整合所有模組化 API
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# 載入環境變數
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

# ============ AI Reports API ============
@app.route('/api/ai-reports', methods=['GET'])
def get_ai_reports():
    try:
        report_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 30))
        
        conn = get_db()
        cursor = conn.cursor()
        
        if report_type == 'all':
            cursor.execute("""
                SELECT id, report_type, report_title, report_content, market_data, created_at, generated_by
                FROM ai_reports
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        else:
            cursor.execute("""
                SELECT id, report_type, report_title, report_content, market_data, created_at, generated_by
                FROM ai_reports
                WHERE report_type = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (report_type, limit))
        
        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row[0],
                'report_type': row[1],
                'title': row[2],
                'content': row[3],
                'market_data': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'generated_by': row[6]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ Prices API ============
@app.route('/api/prices/<code>', methods=['GET'])
def get_prices(code):
    try:
        market = request.args.get('market', 'tw')
        days = int(request.args.get('days', 100))
        
        conn = get_db()
        cursor = conn.cursor()
        
        table = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        
        cursor.execute(f"""
            SELECT trade_date, open_price, high_price, low_price, close_price, volume
            FROM {table}
            WHERE stock_code = %s
            ORDER BY trade_date ASC
            LIMIT %s
        """, (code, days))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'trade_date': row[0].isoformat() if row[0] else None,
                'open_price': float(row[1]) if row[1] else 0,
                'high_price': float(row[2]) if row[2] else 0,
                'low_price': float(row[3]) if row[3] else 0,
                'close_price': float(row[4]) if row[4] else 0,
                'volume': int(row[5]) if row[5] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ Indicators API ============
@app.route('/api/indicators/<code>/ma', methods=['GET'])
def get_ma(code):
    market = request.args.get('market', 'tw')
    period = int(request.args.get('period', 20))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT trade_date, ma
            FROM technical_indicators
            WHERE stock_code = %s AND market = %s AND period = %s
            ORDER BY trade_date ASC
        """, (code, market, period))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'trade_date': row[0].isoformat() if row[0] else None,
                'ma': float(row[1]) if row[1] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ Signals API ============
@app.route('/api/signals/<code>', methods=['GET'])
def get_signals(code):
    market = request.args.get('market', 'tw')
    days = int(request.args.get('days', 100))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 獲取MA5和MA20數據
        cursor.execute("""
            SELECT ti5.trade_date, ti5.ma as ma5, ti20.ma as ma20
            FROM (SELECT * FROM technical_indicators WHERE stock_code = %s AND market = %s AND period = 5 ORDER BY trade_date ASC LIMIT %s) ti5
            LEFT JOIN (SELECT * FROM technical_indicators WHERE stock_code = %s AND market = %s AND period = 20) ti20
            ON ti5.trade_date = ti20.trade_date AND ti5.stock_code = ti20.stock_code
            WHERE ti5.ma IS NOT NULL AND ti20.ma IS NOT NULL
            ORDER BY ti5.trade_date ASC
        """, (code, market, days, code, market))
        
        ma_data = cursor.fetchall()
        signals = []
        
        # 檢測黃金/死亡交叉
        for i in range(1, len(ma_data)):
            prev_ma5, prev_ma20 = float(ma_data[i-1][1] or 0), float(ma_data[i-1][2] or 0)
            curr_ma5, curr_ma20 = float(ma_data[i][1] or 0), float(ma_data[i][2] or 0)
            
            if prev_ma5 <= prev_ma20 and curr_ma5 > curr_ma20:
                signals.append({
                    'date': ma_data[i][0].isoformat(),
                    'type': 'golden_cross',
                    'description': 'MA5上穿MA20',
                    'action': 'buy',
                    'position': 'belowBar'
                })
            elif prev_ma5 >= prev_ma20 and curr_ma5 < curr_ma20:
                signals.append({
                    'date': ma_data[i][0].isoformat(),
                    'type': 'death_cross',
                    'description': 'MA5下穿MA20',
                    'action': 'sell',
                    'position': 'aboveBar'
                })
        
        # 獲取RSI數據
        cursor.execute("""
            SELECT trade_date, rsi
            FROM technical_indicators
            WHERE stock_code = %s AND market = %s AND rsi IS NOT NULL
            ORDER BY trade_date ASC
            LIMIT %s
        """, (code, market, days))
        
        for row in cursor.fetchall():
            rsi = float(row[1]) if row[1] else 50
            if rsi >= 70:
                signals.append({
                    'date': row[0].isoformat(),
                    'type': 'rsi_overbought',
                    'description': f'RSI超買 ({rsi:.1f})',
                    'action': 'sell',
                    'position': 'aboveBar'
                })
            elif rsi <= 30:
                signals.append({
                    'date': row[0].isoformat(),
                    'type': 'rsi_oversold',
                    'description': f'RSI超賣 ({rsi:.1f})',
                    'action': 'buy',
                    'position': 'belowBar'
                })
        
        cursor.close()
        conn.close()
        
        return jsonify({'signals': sorted(signals, key=lambda x: x['date'])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 簡化 API Server 啟動")
    print("端口: 5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)
