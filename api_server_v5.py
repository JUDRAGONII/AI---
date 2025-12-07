"""
API Server V5 - 完整版股價深度分析系統
整合：基礎API + 深度分析 + 技術指標 + AI報告
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path

# 添加計算器路徑
sys.path.insert(0, str(Path(__file__).parent))
from calculators.position_analyzer import PositionAnalyzer
from calculators.technical_indicators import TechnicalIndicators

# 導入籌碼API
from chips_api import chips_api
# 導入宏觀與匯率API
from macro_api import macro_bp
# 導入週期與情緒API
from cycle_sentiment_api import cycle_sentiment_bp
# 導入進階量化分析API
# 導入進階量化分析API
from quant_api import quant_bp
# 導入稅務API
from tax_api import tax_api

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
CORS(app)

# 註冊Blueprint
app.register_blueprint(chips_api)
app.register_blueprint(macro_bp)
app.register_blueprint(cycle_sentiment_bp)
app.register_blueprint(quant_bp)
app.register_blueprint(tax_api, url_prefix='/api/tax')

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

# ========== 健康檢查 ==========
@app.route('/api/market/summary', methods=['GET'])
def market_summary():
    """獲取市場數據庫狀態總覽"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 定義要檢查的表
        queries = {
            'tw_prices': "SELECT COUNT(*) FROM tw_stock_prices",
            'us_prices': "SELECT COUNT(*) FROM us_stock_prices",
            'gold': "SELECT COUNT(*) FROM commodities WHERE type='gold'", # 假設表結構
            'forex': "SELECT COUNT(*) FROM exchange_rates"
        }
        
        stats = {
            'stocks': {'tw_prices': 0, 'us_prices': 0},
            'gold': {'count': 0},
            'forex': {'count': 0},
            'status': 'online'
        }
        
        # 執行查詢
        try:
            cursor.execute(queries['tw_prices'])
            stats['stocks']['tw_prices'] = cursor.fetchone()[0]
        except: pass

        try:
            cursor.execute(queries['us_prices'])
            stats['stocks']['us_prices'] = cursor.fetchone()[0]
        except: pass
        
        try:
            # 檢查表是否存在
            cursor.execute("SELECT to_regclass('commodities')")
            if cursor.fetchone()[0]:
                cursor.execute("SELECT COUNT(*) FROM commodities")
                stats['gold']['count'] = cursor.fetchone()[0]
        except: pass

        try:
            cursor.execute("SELECT to_regclass('exchange_rates')")
            if cursor.fetchone()[0]:
                cursor.execute(queries['forex'])
                stats['forex']['count'] = cursor.fetchone()[0]
        except: pass

        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """API健康檢查"""
    try:
        conn = get_db()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': 'v5.0-深度分析版',
            'database': 'connected',
            'features': ['depth_analysis', 'technical_indicators', 'ai_reports', 'signals']
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# ========== 股價深度分析 ==========
@app.route('/api/analysis/depth/<stock_code>', methods=['GET'])
def depth_analysis(stock_code):
    """
    股價深度分析（整合位階、趨勢、量價、技術指標）
    Query Parameters:
        market: 'tw' or 'us' (預設 'tw')
    """
    market = request.args.get('market', 'tw')
    
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 獲取價格與成交量數據
        table_name = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        cursor.execute(f"""
            SELECT trade_date, high_price, low_price, close_price, volume
            FROM {table_name}
            WHERE stock_code = %s
            ORDER BY trade_date DESC
            LIMIT 252
        """, (stock_code,))
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not data:
            return jsonify({'error': f'找不到 {stock_code} 的數據'}), 404
        
        # 轉換為Series（反轉順序，從舊到新）
        data = list(reversed(data))
        prices = pd.Series([float(d['close_price']) for d in data])
        highs = pd.Series([float(d['high_price']) for d in data])
        lows = pd.Series([float(d['low_price']) for d in data])
        volumes = pd.Series([int(d['volume']) for d in data])
        
        # 使用計算器
        analyzer = PositionAnalyzer()
        tech_calc = TechnicalIndicators()
        
        # 1. 位階分析
        position_level = analyzer.calculate_position_level(prices)
        
        # 2. 趨勢分析
        trend = analyzer.analyze_trend(prices)
        
        # 3. 量價關係
        volume_price = analyzer.analyze_volume_price_relation(prices, volumes)
        
        # 4. 技術指標
        rsi = tech_calc.calculate_rsi(prices)
        macd_line, signal_line, histogram = tech_calc.calculate_macd(prices)
        k, d = tech_calc.calculate_kd(highs, lows, prices)
        
        # 整理技術指標訊號
        technical_signals = {
            'rsi': {
                'value': float(rsi.iloc[-1]) if len(rsi) > 0 else 50,
                'signal': tech_calc.get_signal_interpretation('rsi', rsi.iloc[-1] if len(rsi) > 0 else 50)['signal']
            },
            'macd': {
                'value': float(macd_line.iloc[-1]) if len(macd_line) > 0 else 0,
                'signal': '多頭訊號' if (len(histogram) > 0 and histogram.iloc[-1] > 0) else '空頭訊號'
            },
            'kd': {
                'k': float(k.iloc[-1]) if len(k) > 0 else 50,
                'd': float(d.iloc[-1]) if len(d) > 0 else 50
            }
        }
        
        # 5. 綜合判斷
        judgment = analyzer.comprehensive_judgment(
            position_level,
            trend,
            volume_price,
            technical_signals
        )
        
        # 組裝返回結果
        result = {
            'stock_code': stock_code,
            'market': market,
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(data),
            'position_analysis': position_level,
            'trend_analysis': trend,
            'volume_price_relation': volume_price,
            'technical_signals': technical_signals,
            'comprehensive_judgment': judgment
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

# ========== AI 報告 ==========
@app.route('/api/ai-reports', methods=['GET'])
def get_ai_reports():
    """獲取AI報告列表"""
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

# ========== 價格數據 ==========
@app.route('/api/prices/<code>', methods=['GET'])
def get_prices(code):
    """獲取股價數據"""
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

# ========== 技術指標 ==========
@app.route('/api/indicators/<code>/ma', methods=['GET'])
def get_ma(code):
    """獲取移動平均"""
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

# ========== 訊號 ==========
@app.route('/api/signals/<code>', methods=['GET'])
def get_signals(code):
    """獲取交易訊號（黃金交叉、死亡交叉、RSI超買超賣）"""
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
    port = int(os.getenv('API_PORT', 5000))
    
    print("="*60)
    print("🚀 API Server V5 啟動（深度分析版）")
    print("="*60)
    print(f"📡 http://localhost:{port}")
    print(f"💾 PostgreSQL@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print("="*60)
    print("📋 API端點清單:")
    print("  【系統】")
    print("    GET  /api/health")
    print("  【深度分析】🆕")
    print("    GET  /api/analysis/depth/<code>")
    print("  【AI報告】")
    print("    GET  /api/ai-reports")
    print("  【價格數據】")
    print("    GET  /api/prices/<code>")
    print("  【技術指標】")
    print("    GET  /api/indicators/<code>/ma")
    print("  【交易訊號】")
    print("    GET  /api/signals/<code>")
    print("  【籌碼分析】🆕")
    print("    GET  /api/chips/<code>/institutional")
    print("    GET  /api/chips/<code>/margin")
    print("    GET  /api/chips/<code>/all")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
