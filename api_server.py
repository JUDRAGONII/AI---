"""
Flask API 服務 - 整合所有後端模組
提供 RESTful API 給前端應用使用
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# 導入自定義模組
from calculators import FactorEngine
from calculators.technical_indicators import TechnicalIndicators
from ai.report_generator import DailyReportGenerator, DecisionTemplateGenerator
from api_clients import TWStockClient, USStockClient
from data_loader.database_connector import DatabaseConnector

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化
db = DatabaseConnector()
factor_engine = FactorEngine()
tw_client = TWStockClient()
us_client = USStockClient()
daily_report_gen = DailyReportGenerator()
decision_gen = DecisionTemplateGenerator()

# ============ 健康檢查 ============
@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# ============ 因子分析 API ============
@app.route('/api/factors/<stock_code>', methods=['GET'])
def get_factor_scores(stock_code):
    """獲取個股因子分數"""
    try:
        market = request.args.get('market', 'tw')
        
        # 從資料庫獲取最新價格
        query = f"""
        SELECT close_price 
        FROM {'tw_stock_prices' if market == 'tw' else 'us_stock_prices'}
        WHERE stock_code = %s
        ORDER BY trade_date DESC
        LIMIT 1
        """
        result = db.execute_query(query, (stock_code,))
        
        if not result:
            return jsonify({'error': '找不到股票資料'}), 404
        
        current_price = result[0]['close_price']
        
        # 計算因子分數
        scores = factor_engine.calculate_all_factors(
            stock_code, 
            current_price, 
            market,
            save_to_db=False
        )
        
        return jsonify({
            'stock_code': stock_code,
            'market': market,
            'current_price': current_price,
            'scores': scores,
            'calculated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/factors/<stock_code>/history', methods=['GET'])
def get_factor_history(stock_code):
    """獲取個股歷史因子分數"""
    try:
        days = request.args.get('days', 30, type=int)
        market = request.args.get('market', 'tw')
        
        query = """
        SELECT * FROM quant_scores
        WHERE stock_code = %s AND market = %s
        ORDER BY calculation_date DESC
        LIMIT %s
        """
        
        results = db.execute_query(query, (stock_code, market, days))
        
        return jsonify({
            'stock_code': stock_code,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ AI 報告 API ============
@app.route('/api/ai/daily-report', methods=['GET', 'POST'])
def ai_daily_report():
    """生成或獲取每日戰略報告"""
    if request.method == 'POST':
        # 生成新報告
        try:
            report = daily_report_gen.generate_daily_report()
            return jsonify({
                'success': True,
                'report': report
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        # 獲取最新報告
        try:
            query = """
            SELECT * FROM ai_reports
            WHERE report_type = 'daily_strategy'
            ORDER BY created_at DESC
            LIMIT 1
            """
            result = db.execute_query(query)
            
            if result:
                return jsonify(result[0])
            else:
                return jsonify({'message': '尚無報告'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/ai/decision-template/<stock_code>', methods=['POST'])
def ai_decision_template(stock_code):
    """生成個股決策模板"""
    try:
        market = request.json.get('market', 'tw')
        report = decision_gen.generate_decision_template(stock_code, market)
        
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ TDCC 籌碼 API ============
@app.route('/api/tdcc/<stock_code>', methods=['GET'])
def get_tdcc_data(stock_code):
    """獲取TDCC股權分散資料"""
    try:
        days = request.args.get('days', 52, type=int)
        
        query = """
        SELECT * FROM shareholder_dispersion
        WHERE stock_code = %s
        ORDER BY data_date DESC
        LIMIT %s
        """
        
        results = db.execute_query(query, (stock_code, days))
        
        return jsonify({
            'stock_code': stock_code,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tdcc/<stock_code>/latest', methods=['GET'])
def get_latest_tdcc(stock_code):
    """獲取最新TDCC資料"""
    try:
        query = """
        SELECT * FROM shareholder_dispersion
        WHERE stock_code = %s
        ORDER BY data_date DESC
        LIMIT 1
        """
        
        result = db.execute_query(query, (stock_code,))
        
        if result:
            return jsonify(result[0])
        else:
            return jsonify({'message': '找不到資料'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 價格資料 API ============
@app.route('/api/prices/<stock_code>', methods=['GET'])
def get_stock_prices(stock_code):
    """獲取股價資料"""
    try:
        market = request.args.get('market', 'tw')
        days = request.args.get('days', 252, type=int)
        
        table = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        
        query = f"""
        SELECT * FROM {table}
        WHERE stock_code = %s
        ORDER BY trade_date DESC
        LIMIT %s
        """
        
        results = db.execute_query(query, (stock_code, days))
        
        return jsonify({
            'stock_code': stock_code,
            'market': market,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 技術指標 API ============
@app.route('/api/indicators/<stock_code>', methods=['GET'])
def get_technical_indicators(stock_code):
    """計算技術指標"""
    try:
        market = request.args.get('market', 'tw')
        days = request.args.get('days', 100, type=int)
        
        # 獲取價格資料
        table = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        query = f"""
        SELECT trade_date, close_price, high_price, low_price, volume
        FROM {table}
        WHERE stock_code = %s
        ORDER BY trade_date ASC
        LIMIT %s
        """
        
        price_data = db.execute_query(query, (stock_code, days))
        
        if not price_data:
            return jsonify({'error': '找不到價格資料'}), 404
        
        # 計算技術指標
        indicators = TechnicalIndicators.calculate_all_indicators(price_data)
        
        return jsonify({
            'stock_code': stock_code,
            'indicators': indicators
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 股票清單 API ============
@app.route('/api/stocks/list', methods=['GET'])
def get_stock_list():
    """獲取股票清單"""
    try:
        market = request.args.get('market', 'tw')
        
        if market == 'tw':
            query = """
            SELECT stock_code, stock_name, industry 
            FROM tw_stock_info
            ORDER BY stock_code
            """
        else:
            query = """
            SELECT stock_code, stock_name, exchange
            FROM us_stock_info
            ORDER BY stock_code
            """
        
        results = db.execute_query(query)
        
        return jsonify({
            'market': market,
            'count': len(results),
            'stocks': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 搜尋 API ============
@app.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """搜尋股票"""
    try:
        query_text = request.args.get('q', '')
        market = request.args.get('market', 'tw')
        
        if not query_text:
            return jsonify({'error': '請提供搜尋關鍵字'}), 400
        
        if market == 'tw':
            query = """
            SELECT stock_code, stock_name, industry
            FROM tw_stock_info
            WHERE stock_code LIKE %s OR stock_name LIKE %s
            LIMIT 20
            """
        else:
            query = """
            SELECT stock_code, stock_name, exchange
            FROM us_stock_info
            WHERE stock_code LIKE %s OR stock_name LIKE %s
            LIMIT 20
            """
        
        search_pattern = f'%{query_text}%'
        results = db.execute_query(query, (search_pattern, search_pattern))
        
        return jsonify({
            'query': query_text,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API配置管理 ============
@app.route('/api/config/sync-api-keys', methods=['POST'])
def sync_api_keys():
    """同步API金鑰到後端配置"""
    try:
        data = request.get_json()
        
        # 驗證請求
        if not data:
            return jsonify({'success': False, 'message': '無效的請求'}), 400
        
        # 更新.env檔案
        env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
        updated_keys = []
        
        # 讀取現有.env
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        # API金鑰映射（前端key → 後端env變數）
        key_mapping = {
            'gemini': 'GEMINI_API_KEY',
            'alphaVantage': 'ALPHA_VANTAGE_API_KEY',
            'tiingo': 'TIINGO_API_KEY',
            'finnhub': 'FINNHUB_API_KEY',
            'fred': 'FRED_API_KEY',
            'fmp': 'FMP_API_KEY',
            'goldApi': 'GOLD_API_KEY',
            'exchangeRate': 'EXCHANGE_RATE_API_KEY',
            'marketaux': 'MARKETAUX_API_KEY'
        }
        
        # 更新API金鑰
        for frontend_key, backend_key in key_mapping.items():
            if frontend_key in data and data[frontend_key]:
                env_vars[backend_key] = data[frontend_key]
                updated_keys.append(frontend_key)
        
        # 寫回.env檔案
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')
        
        # 重新載入環境變數
        load_dotenv(env_path, override=True)
        
        return jsonify({
            'success': True,
            'message': f'成功同步{len(updated_keys)}個API金鑰',
            'synced_keys': updated_keys
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'同步失敗: {str(e)}'
        }), 500


@app.route('/api/config/api-keys', methods=['GET'])
def get_api_keys_status():
    """獲取API金鑰配置狀態"""
    try:
        keys_status = {}
        
        # API金鑰映射
        key_mapping = {
            'gemini': 'GEMINI_API_KEY',
            'alphaVantage': 'ALPHA_VANTAGE_API_KEY',
            'tiingo': 'TIINGO_API_KEY',
            'finnhub': 'FINNHUB_API_KEY',
            'fred': 'FRED_API_KEY',
            'fmp': 'FMP_API_KEY',
            'goldApi': 'GOLD_API_KEY',
            'exchangeRate': 'EXCHANGE_RATE_API_KEY',
            'marketaux': 'MARKETAUX_API_KEY'
        }
        
        # 檢查each key的配置狀態
        for frontend_key, backend_key in key_mapping.items():
            api_key = os.getenv(backend_key, '')
            # 檢查是否已配置（不是範例值）
            is_configured = (api_key and 
                           'your_' not in api_key.lower() and 
                           '_here' not in api_key.lower() and
                           len(api_key) > 10)
            
            if is_configured:
                keys_status[frontend_key] = {
                    'configured': True,
                    'masked_key': api_key[:6] + '***' if len(api_key) > 6 else '***'
                }
            else:
                keys_status[frontend_key] = {
                    'configured': False
                }
        
        return jsonify(keys_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 錯誤處理 ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API 端點不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '伺服器內部錯誤'}), 500

# ============ 主程式 ============
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 API 服務啟動於 http://localhost:{port}")
    print(f"📊 資料庫連接: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print(f"🔧 除錯模式: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
