"""
宏觀與匯率分析API
提供總體經濟與外匯分析端點
"""
from flask import Blueprint, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
import sys

# 添加calculators到路徑
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from calculators.macro_analyzer import get_macro_analysis
from calculators.forex_analyzer import get_forex_analysis

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# 創建Blueprint
macro_bp = Blueprint('macro', __name__)

def get_db():
    """獲取資料庫連接"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

@macro_bp.route('/api/macro/economy', methods=['GET'])
def get_economy_analysis():
    """
    獲取總體經濟分析
    查詢參數：
    - market: tw或us（預設：tw）
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        result = get_macro_analysis(conn, market)
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@macro_bp.route('/api/macro/forex', methods=['GET'])
def get_forex_data():
    """
    獲取外匯分析（USD/TWD）
    查詢參數：
    - market: tw或us（預設：tw）- 影響評估視角
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        result = get_forex_analysis(conn, market)
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@macro_bp.route('/api/macro/combined', methods=['GET'])
def get_combined_macro():
    """
    獲取綜合宏觀分析（經濟+匯率）
    查詢參數：
    - market: tw或us（預設：tw）
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        
        # 獲取兩組數據
        economy = get_macro_analysis(conn, market)
        forex = get_forex_analysis(conn, market)
        
        conn.close()
        
        # 組合結果
        return jsonify({
            'success': True,
            'data': {
                'market': market,
                'economy': economy,
                'forex': forex,
                '综合評估': {
                    '經濟評分': economy['overall_sentiment']['score'],
                    '匯率評分': forex['綜合評估']['評分'],
                    '整體狀態': '利多' if economy['overall_sentiment']['score'] > 70 and forex['綜合評估']['評分'] > 70 else '觀望'
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("宏觀與匯率分析API測試")
    print("=" * 60)
    print("API端點：")
    print("  GET /api/macro/economy?market=tw")
    print("  GET /api/macro/forex?market=tw")
    print("  GET /api/macro/combined?market=tw")
    print("=" * 60)
