"""
週期與情緒分析API
提供週期定位與市場情緒分析端點
"""
from flask import Blueprint, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from calculators.cycle_analyzer import get_cycle_analysis
from calculators.sentiment_analyzer import get_sentiment_analysis

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

cycle_sentiment_bp = Blueprint('cycle_sentiment', __name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

@cycle_sentiment_bp.route('/api/analysis/cycle', methods=['GET'])
def get_cycle_data():
    """
    獲取週期性定位分析
    查詢參數：
    - market: tw或us（預設：tw）
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        result = get_cycle_analysis(conn, market)
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

@cycle_sentiment_bp.route('/api/analysis/sentiment', methods=['GET'])
def get_sentiment_data():
    """
    獲取市場情緒分析
    查詢參數：
    - market: tw或us（預設：tw）
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        result = get_sentiment_analysis(conn, market)
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

@cycle_sentiment_bp.route('/api/analysis/market_pulse', methods=['GET'])
def get_market_pulse():
    """
    獲取市場脈搏（週期+情緒綜合）
    查詢參數：
    - market: tw或us（預設：tw）
    """
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        
        cycle = get_cycle_analysis(conn, market)
        sentiment = get_sentiment_analysis(conn, market)
        
        conn.close()
        
        # 綜合評估
        cycle_score = cycle['綜合評估']['綜合評分']
        sentiment_score = sentiment['恐懼貪婪指數']['指數']
        
        # 計算市場健康度
        health_score = (cycle_score * 0.6 + sentiment_score * 0.4)
        
        if health_score >= 70:
            health = '健康'
            signal = 'positive'
        elif health_score >= 50:
            health = '中性'
            signal = 'neutral'
        else:
            health = '謹慎'
            signal = 'negative'
        
        return jsonify({
            'success': True,
            'data': {
                'market': market,
                'cycle_analysis': cycle,
                'sentiment_analysis': sentiment,
                'market_health': {
                    'score': round(health_score, 1),
                    'status': health,
                    'signal': signal,
                    'interpretation': f'市場整體{health}，建議{cycle["綜合評估"]["投資策略"]}'
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("週期與情緒分析API測試")
    print("=" * 60)
    print("API端點：")
    print("  GET /api/analysis/cycle?market=tw")
    print("  GET /api/analysis/sentiment?market=tw")
    print("  GET /api/analysis/market_pulse?market=tw")
    print("=" * 60)
