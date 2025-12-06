# ========== 訊號標註端點 ==========

@app.route('/api/signals/<stock_code>', methods=['GET'])
def get_signals(stock_code):
    """獲取技術訊號（黃金交叉、死亡交叉、RSI超買超賣）"""
    try:
        market = request.args.get('market', 'tw')
        days = request.args.get('days', 100, type=int)
        
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 獲取MA數據
        cursor.execute("""
            SELECT trade_date, value as ma5
            FROM technical_indicators
            WHERE stock_code = %s AND market = %s AND indicator_type = 'MA'
              AND parameters->>'period' = '5'
            ORDER BY trade_date ASC
            LIMIT %s
        """, (stock_code, market, days))
        ma5_data = {row['trade_date']: float(row['ma5']) for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT trade_date, value as ma20
            FROM technical_indicators
            WHERE stock_code = %s AND market = %s AND indicator_type = 'MA'
              AND parameters->>'period' = '20'
            ORDER BY trade_date ASC
            LIMIT %s
        """, (stock_code, market, days))
        ma20_data = {row['trade_date']: float(row['ma20']) for row in cursor.fetchall()}
        
        # 獲取RSI數據
        cursor.execute("""
            SELECT trade_date, value as rsi
            FROM technical_indicators
            WHERE stock_code = %s AND market = %s AND indicator_type = 'RSI'
            ORDER BY trade_date ASC
            LIMIT %s
        """, (stock_code, market, days))
        rsi_data = {row['trade_date']: float(row['rsi']) for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        signals = []
        
        # 黃金交叉/死亡交叉檢測
        dates = sorted(set(ma5_data.keys()) & set(ma20_data.keys()))
        for i in range(1, len(dates)):
            prev_date = dates[i-1]
            curr_date = dates[i]
            
            ma5_prev = ma5_data[prev_date]
            ma5_curr = ma5_data[curr_date]
            ma20_prev = ma20_data[prev_date]
            ma20_curr = ma20_data[curr_date]
            
            # 黃金交叉：MA5上穿MA20
            if ma5_prev <= ma20_prev and ma5_curr > ma20_curr:
                signals.append({
                    'date': str(curr_date),
                    'type': 'golden_cross',
                    'description': 'MA5上穿MA20',
                    'action': 'buy',
                    'position': 'belowBar'
                })
            
            # 死亡交叉：MA5下穿MA20
            if ma5_prev >= ma20_prev and ma5_curr < ma20_curr:
                signals.append({
                    'date': str(curr_date),
                    'type': 'death_cross',
                    'description': 'MA5下穿MA20',
                    'action': 'sell',
                    'position': 'aboveBar'
                })
        
        # RSI超買超賣檢測
        for date, rsi in rsi_data.items():
            if rsi >= 70:
                signals.append({
                    'date': str(date),
                    'type': 'rsi_overbought',
                    'description': f'RSI超買 ({rsi:.1f})',
                    'action': 'sell',
                    'position': 'aboveBar'
                })
            elif rsi <= 30:
                signals.append({
                    'date': str(date),
                    'type': 'rsi_oversold',
                    'description': f'RSI超賣 ({rsi:.1f})',
                    'action': 'buy',
                    'position': 'belowBar'
                })
        
        # 按日期排序
        signals.sort(key=lambda x: x['date'])
        
        return jsonify({'signals': signals})
        
    except Exception as e:
        print(f"獲取訊號失敗: {e}")
        return jsonify({'error': str(e)}), 500
