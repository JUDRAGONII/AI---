"""
擴展版Flask API伺服器
包含核心數據查詢端點
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from data_loader import DatabaseConnector
from datetime import datetime
import os
from dotenv import load_dotenv
from loguru import logger

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
CORS(app)

# 初始化資料庫連接
db = DatabaseConnector()

# ============ 健康檢查 ============
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    db_status = db.test_connection()
    
    return jsonify({
        'status': 'healthy' if db_status else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-lite-extended',
        'database': {
            'connected': db_status,
            'name': os.getenv('DB_NAME', 'quant_db')
        },
        'message': 'API伺服器運行中（擴展版）'
    })

# ============ 股票資訊 ============
@app.route('/api/stocks/list', methods=['GET'])
def get_stock_list():
    """獲取股票列表"""
    try:
        market = request.args.get('market', 'tw')
        limit = request.args.get('limit', 100, type=int)
        
        table_name = 'tw_stock_info' if market == 'tw' else 'us_stock_info'
        
        stocks = db.execute_query(f"""
            SELECT * FROM {table_name}
            ORDER BY stock_code
            LIMIT %s
        """, (limit,))
        
        return jsonify({
            'market': market,
            'count': len(stocks),
            'stocks': stocks
        })
    except Exception as e:
        logger.error(f"❌ 獲取股票列表失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stocks/<code>', methods=['GET'])
def get_stock_detail(code):
    """獲取股票詳情"""
    try:
        market = request.args.get('market', 'tw')
        table_name = 'tw_stock_info' if market == 'tw' else 'us_stock_info'
        
        stock = db.execute_query(f"""
            SELECT * FROM {table_name}
            WHERE stock_code = %s
        """, (code,), fetch_one=True)
        
        if not stock:
            return jsonify({'error': f'找不到股票 {code}'}), 404
        
        return jsonify(stock)
    except Exception as e:
        logger.error(f"❌ 獲取股票詳情失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ 價格資料 ============
@app.route('/api/prices/<code>', methods=['GET'])
def get_stock_prices(code):
    """獲取股票價格歷史"""
    try:
        market = request.args.get('market', 'tw')
        days = request.args.get('days', 30, type=int)
        
        table_name = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        
        prices = db.execute_query(f"""
            SELECT * FROM {table_name}
            WHERE stock_code = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (code, days))
        
        return jsonify({
            'stock_code': code,
            'market': market,
            'count': len(prices),
            'data': prices
        })
    except Exception as e:
        logger.error(f"❌ 獲取價格數據失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ 資料庫管理 ============
@app.route('/api/database/tables', methods=['GET'])
def get_tables():
    """獲取所有資料表"""
    try:
        tables = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        return jsonify({
            'count': len(tables),
            'tables': [t['table_name'] for t in tables]
        })
    except Exception as e:
        logger.error(f"❌ 獲取資料表失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ API配置管理 ============
@app.route('/api/config/api-keys', methods=['GET'])
def get_api_keys_status():
    """獲取API金鑰配置狀態"""
    try:
        keys_status = {}
        
        key_mapping = {
            'gemini': 'GEMINI_API_KEY',
            'alphaVantage': 'ALPHA_VANTAGE_API_KEY',
            'tiingo': 'TIINGO_API_KEY',
            'finnhub': 'FINNHUB_API_KEY',
            'fred': 'FRED_API_KEY',
        }
        
        for frontend_key, backend_key in key_mapping.items():
            api_key = os.getenv(backend_key, '')
            is_configured = api_key and len(api_key) > 10 and 'your_' not in api_key.lower()
            
            if is_configured:
                keys_status[frontend_key] = {
                    'configured': True,
                    'masked_key': api_key[:6] + '***'
                }
            else:
                keys_status[frontend_key] = {'configured': False}
        
        return jsonify(keys_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/sync-api-keys', methods=['POST'])
def sync_api_keys():
    """同步API金鑰"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求'}), 400
        
        # 這裡簡化處理，實際應該寫入.env文件
        return jsonify({
            'success': True,
            'message': 'API金鑰同步功能（簡化版）'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============ 錯誤處理 ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端點不存在'}), 404
        logger.info("✅ 資料庫連接已關閉")
