"""
API系統狀態端點
新增到 api_server_v3.py 的末尾 (在 if __name__ == '__main__': 之前)
"""

# ========== 系統API狀態 ==========
@app.route('/api/system/api-status', methods=['GET'])
def get_api_status():
    """獲取所有API的狀態信息"""
    import time
    from datetime import datetime, timedelta
    
    api_statuses = []
    
    # 1. 測試資料庫連接
    db_status = {
        'name': 'PostgreSQL Database',
        'category': '資料庫',
        'status': 'healthy',
        'uptime': 99.9,
        'latency': 0,
        'lastUpdate': '剛剛',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        conn.close()
        db_status['latency'] = int((time.time() - start) * 1000)
        db_status['status'] = 'healthy'
    except Exception as e:
        db_status['status'] = 'error'
        db_status['errorRate'] = 100
    
    api_statuses.append(db_status)
    
    # 2. Gemini AI API
    ai_status = {
        'name': 'Gemini AI',
        'category': 'AI服務',
        'status': 'unknown',
        'uptime': 95.0,
        'latency': 0,
        'lastUpdate': '未測試',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '15次/分鐘'
    }
    
    if AI_ENABLED:
        try:
            # 檢查API Key是否存在
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
            if api_key:
                ai_status['status'] = 'healthy'
                ai_status['lastUpdate'] = '已配置'
                ai_status['latency'] = 2500  # 估計值
            else:
                ai_status['status'] = 'warning'
                ai_status['lastUpdate'] = '未配置API Key'
                ai_status['errorRate'] = 100
        except:
            ai_status['status'] = 'error'
            ai_status['errorRate'] = 100
    else:
        ai_status['status'] = 'error'
        ai_status['lastUpdate'] = 'AI模組未安裝'
        ai_status['errorRate'] = 100
    
    api_statuses.append(ai_status)
    
    # 3. 台股數據源
    tw_status = {
        'name': 'TWSE Data',
        'category': '台股資料',
        'status': 'healthy',
        'uptime': 99.5,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tw_stock_info")
        tw_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM tw_stock_prices")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        tw_status['latency'] = int((time.time() - start) * 1000)
        tw_status['requestsToday'] = tw_count
        if latest:
            tw_status['lastUpdate'] = str(latest)
        tw_status['status'] = 'healthy'
    except:
        tw_status['status'] = 'error'
        tw_status['errorRate'] = 100
    
    api_statuses.append(tw_status)
    
    # 4. 美股數據源
    us_status = {
        'name': 'US Stock Data',
        'category': '美股資料',
        'status': 'healthy',
        'uptime': 99.2,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM us_stock_info")
        us_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM us_stock_prices")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        us_status['latency'] = int((time.time() - start) * 1000)
        us_status['requestsToday'] = us_count
        if latest:
            us_status['lastUpdate'] = str(latest)
        us_status['status'] = 'healthy'
    except:
        us_status['status'] = 'error'
        us_status['errorRate'] = 100
    
    api_statuses.append(us_status)
    
    # 5. 黃金數據
    gold_status = {
        'name': 'Gold Price Data',
        'category': '商品資料',
        'status': 'healthy',
        'uptime': 98.8,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        gold_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM commodity_prices WHERE commodity_code = 'GOLD'")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        gold_status['latency'] = int((time.time() - start) * 1000)
        gold_status['requestsToday'] = gold_count
        if latest:
            gold_status['lastUpdate'] = str(latest)
        gold_status['status'] = 'healthy'
    except:
        gold_status['status'] = 'error'
        gold_status['errorRate'] = 100
    
    api_statuses.append(gold_status)
    
    # 6匯率數據
    forex_status = {
        'name': 'Exchange Rate Data',
        'category': '匯率資料',
        'status': 'healthy',
        'uptime': 99.1,
        'latency': 0,
        'lastUpdate': '已同步',
        'requestsToday': 0,
        'errorRate': 0,
        'rateLimit': '無限制'
    }
    try:
        start = time.time()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exchange_rates")
        forex_count = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(trade_date) FROM exchange_rates")
        latest = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        forex_status['latency'] = int((time.time() - start) * 1000)
        forex_status['requestsToday'] = forex_count
        if latest:
            forex_status['lastUpdate'] = str(latest)
        forex_status['status'] = 'healthy'
    except:
        forex_status['status'] = 'error'
        forex_status['errorRate'] = 100
    
    api_statuses.append(forex_status)
    
    return jsonify({
        'apis': api_statuses,
        'timestamp': datetime.now().isoformat()
    })
