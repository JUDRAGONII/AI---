"""
籌碼分析 API
提供三大法人、融資融券相關數據查詢
"""
from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2 import extras
import os
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from calculators.institutional_analyzer import InstitutionalAnalyzer
from calculators.margin_analyzer import MarginAnalyzer

chips_api = Blueprint('chips_api', __name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

@chips_api.route('/api/chips/<stock_code>/institutional', methods=['GET'])
def get_institutional(stock_code):
    """
    獲取三大法人買賣超分析
    Query Parameters:
        days: 分析天數 (預設 20)
    """
    days = int(request.args.get('days', 20))
    
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 獲取三大法人交易數據
        cursor.execute("""
            SELECT trade_date, foreign_buy, foreign_sell, trust_buy, trust_sell,
                   dealer_buy, dealer_sell, close_price
            FROM institutional_trades
            WHERE stock_code = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (stock_code, days))
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not data:
            return jsonify({'error': f'找不到 {stock_code} 的三大法人數據'}), 404
        
        # 轉換為DataFrame並分析
        df = pd.DataFrame(data)
        df = df.sort_values('trade_date')  # 由舊到新排序
        
        analyzer = InstitutionalAnalyzer()
        analysis = analyzer.analyze_daily_trades(df, days=min(days, len(df)))
        
        return jsonify({
            'stock_code': stock_code,
            'analysis_days': days,
            'data_points': len(data),
            'analysis': analysis
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@chips_api.route('/api/chips/<stock_code>/margin', methods=['GET'])
def get_margin(stock_code):
    """
    獲取融資融券分析
    """
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 獲取融資融券數據
        cursor.execute("""
            SELECT trade_date, margin_balance, margin_quota, short_balance, short_quota
            FROM margin_trading
            WHERE stock_code = %s
            ORDER BY trade_date DESC
            LIMIT 30
        """, (stock_code,))
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not data:
            return jsonify({'error': f'找不到 {stock_code} 的融資融券數據'}), 404
        
        # 轉換為DataFrame並分析
        df = pd.DataFrame(data)
        df = df.sort_values('trade_date')  # 由舊到新排序
        
        analyzer = MarginAnalyzer()
        analysis = analyzer.analyze_margin_trading(df)
        
        return jsonify({
            'stock_code': stock_code,
            'data_points': len(data),
            'analysis': analysis
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@chips_api.route('/api/chips/<stock_code>/all', methods=['GET'])
def get_all_chips(stock_code):
    """
    獲取完整籌碼分析（三大法人 + 融資融券）
    """
    days = int(request.args.get('days', 20))
    
    try:
        # 獲取三大法人數據
        institutional_response = get_institutional(stock_code)
        institutional_data = institutional_response.get_json() if institutional_response.status_code == 200 else None
        
        # 獲取融資融券數據
        margin_response = get_margin(stock_code)
        margin_data = margin_response.get_json() if margin_response.status_code == 200 else None
        
        if not institutional_data and not margin_data:
            return jsonify({'error': f'找不到 {stock_code} 的籌碼數據'}), 404
        
        return jsonify({
            'stock_code': stock_code,
            'institutional': institutional_data.get('analysis') if institutional_data else None,
            'margin': margin_data.get('analysis') if margin_data else None
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
