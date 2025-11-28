"""
簡化版Flask API伺服器
僅包含API配置管理端點，用於前後端API金鑰同步測試
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# ============ 健康檢查 ============
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-lite',
        'message': '簡化版API伺服器運行中'
    })

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
        
        print(f"✅ 成功同步 {len(updated_keys)} 個API金鑰")
        for key in updated_keys:
            print(f"   - {key}")
        
        return jsonify({
            'success': True,
            'message': f'成功同步{len(updated_keys)}個API金鑰',
            'synced_keys': updated_keys
        })
        
    except Exception as e:
        print(f"❌ 同步失敗: {str(e)}")
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
    
    print("=" * 60)
    print("🚀 簡化版 API 伺服器啟動")
    print("=" * 60)
    print(f"📡 服務網址: http://localhost:{port}")
    print(f"📊 環境檔案: {os.path.join(os.path.dirname(__file__), 'config', '.env')}")
    print(f"✨ 可用端點:")
    print(f"   - GET  /api/health")
    print(f"   - GET  /api/config/api-keys")
    print(f"   - POST /api/config/sync-api-keys")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
