"""
WebSocket伺服器 - 提供即時市場數據推送
"""

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
import time
from threading import Thread
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_db():
    """獲取資料庫連接"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )


def get_market_data():
    """從資料庫獲取最新市場數據"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 獲取最新黃金價格
        cursor.execute("""
            SELECT close_price, trade_date 
            FROM commodity_prices 
            WHERE commodity_code = 'GOLD' 
            ORDER BY trade_date DESC LIMIT 1
        """)
        gold = cursor.fetchone()
        
        # 獲取最新USD/TWD匯率
        cursor.execute("""
            SELECT rate, trade_date 
            FROM exchange_rates 
            WHERE base_currency = 'USD' AND quote_currency = 'TWD' 
            ORDER BY trade_date DESC LIMIT 1
        """)
        forex = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'gold': float(gold[0]) if gold else None,
            'gold_date': str(gold[1]) if gold else None,
            'usd_twd': float(forex[0]) if forex else None,
            'forex_date': str(forex[1]) if forex else None,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"獲取市場數據錯誤: {e}")
        return None


def background_market_update():
    """背景執行緒：定期推送市場數據更新"""
    while True:
        try:
            data = get_market_data()
            if data:
                socketio.emit('market_update', data, broadcast=True)
                print(f"📡 推送市場更新: Gold=${data['gold']}, USD/TWD={data['usd_twd']}")
            time.sleep(5)  # 每5秒更新一次
        except Exception as e:
            print(f"背景更新錯誤: {e}")
            time.sleep(5)


@socketio.on('connect')
def handle_connect():
    """客戶端連接"""
    print('✅ 客戶端已連接')
    # 立即發送當前市場數據
    data = get_market_data()
    if data:
        emit('market_update', data)


@socketio.on('disconnect')
def handle_disconnect():
    """客戶端斷開"""
    print('❌ 客戶端已斷開')


@socketio.on('subscribe_stock')
def handle_subscribe_stock(data):
    """訂閱特定股票的即時更新"""
    stock_code = data.get('stock_code')
    print(f'📊 訂閱股票: {stock_code}')
    
    # 獲取該股票的最新價格
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        market = data.get('market', 'tw')
        if market == 'tw':
            cursor.execute("""
                SELECT stock_code, close_price, trade_date, volume
                FROM tw_stock_prices
                WHERE stock_code = %s
                ORDER BY trade_date DESC LIMIT 1
            """, (stock_code,))
        else:
            cursor.execute("""
                SELECT symbol, close_price, trade_date, volume
                FROM us_stock_prices
                WHERE symbol = %s
                ORDER BY trade_date DESC LIMIT 1
            """, (stock_code,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            stock_data = {
                'code': result[0],
                'price': float(result[1]),
                'date': str(result[2]),
                'volume': int(result[3]) if result[3] else 0,
                'timestamp': datetime.now().isoformat()
            }
            emit('stock_update', stock_data)
        else:
            emit('error', {'message': f'找不到股票: {stock_code}'})
            
    except Exception as e:
        print(f"訂閱股票錯誤: {e}")
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 WebSocket伺服器啟動")
    print("=" * 60)
    print("📡 Port: 5001")
    print("🔄 即時更新間隔: 5秒")
    print("=" * 60)
    
    # 啟動背景更新執行緒
    update_thread = Thread(target=background_market_update, daemon=True)
    update_thread.start()
    
    # 啟動WebSocket伺服器
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
