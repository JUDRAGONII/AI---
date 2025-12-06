# ========== 交易日誌端點 ==========

def calculate_transaction_fees(market, transaction_type, price, quantity, broker_name='元大證券'):
    """計算交易費用（手續費與稅金）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    # 查詢券商費率
    cursor.execute("""
        SELECT fee_rate, min_fee, discount 
        FROM broker_fees 
        WHERE broker_name = %s AND market = %s
        LIMIT 1
    """, (broker_name, market))
    
    broker_fee_info = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not broker_fee_info:
        # 預設費率
        fee_rate = 0.001425 if market == 'tw' else 0
        min_fee = 20 if market == 'tw' else 0
        discount = 0.6
    else:
        fee_rate = float(broker_fee_info['fee_rate'])
        min_fee = float(broker_fee_info['min_fee'])
        discount = float(broker_fee_info['discount'])
    
    # 計算手續費
    trade_amount = price * quantity
    fee = max(trade_amount * fee_rate * discount, min_fee)
    
    # 計算證交稅（僅台股賣出）
    tax = 0
    if market == 'tw' and transaction_type == 'sell':
        tax = trade_amount * 0.003  # 台股證交稅 0.3%
    
    # 計算總金額
    if transaction_type == 'buy':
        total = trade_amount + fee
    else:  # sell
        total = trade_amount - fee - tax
    
    return {
        'fees': round(fee, 2),
        'tax': round(tax, 2),
        'total_amount': round(total, 2)
    }


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """獲取交易記錄列表"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 查詢參數
        market = request.args.get('market')
        transaction_type = request.args.get('type')
        stock_code = request.args.get('stock_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 50, type=int)
        
        # 構建查詢
        query = "SELECT * FROM transactions WHERE user_id = 1"
        params = []
        
        if market:
            query += " AND market = %s"
            params.append(market)
        if transaction_type:
            query += " AND transaction_type = %s"
            params.append(transaction_type)
        if stock_code:
            query += " AND stock_code = %s"
            params.append(stock_code)
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY transaction_date DESC, created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        transactions = [dict(row) for row in cursor.fetchall()]
        
        # 格式化日期
        for t in transactions:
            t['transaction_date'] = str(t['transaction_date'])
            if t.get('settlement_date'):
                t['settlement_date'] = str(t['settlement_date'])
        
        # 計算統計
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN transaction_type = 'buy' THEN 1 END) as total_buy,
                COUNT(CASE WHEN transaction_type = 'sell' THEN 1 END) as total_sell,
                COALESCE(SUM(fees), 0) as total_fees,
                COALESCE(SUM(tax), 0) as total_tax
            FROM transactions
            WHERE user_id = 1
        """)
        summary = dict(cursor.fetchone())
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'transactions': transactions,
            'summary': summary
        })
        
    except Exception as e:
        print(f"獲取交易記錄失敗: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """新增交易記錄（自動計算費用）"""
    try:
        data = request.get_json()
        
        # 計算費用
        fees_info = calculate_transaction_fees(
            market=data['market'],
            transaction_type=data['transaction_type'],
            price=float(data['price']),
            quantity=int(data['quantity']),
            broker_name=data.get('broker', '元大證券')
        )
        
        # 計算交割日期（T+2）
        from datetime import datetime, timedelta
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d')
        settlement_date = transaction_date + timedelta(days=2)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, stock_code, market, transaction_type, quantity, price, 
             transaction_date, settlement_date, broker, fees, tax, total_amount, notes)
            VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['stock_code'],
            data['market'],
            data['transaction_type'],
            data['quantity'],
            data['price'],
            data['transaction_date'],
            settlement_date,
            data.get('broker', '元大證券'),
            fees_info['fees'],
            fees_info['tax'],
            fees_info['total_amount'],
            data.get('notes', '')
        ))
        
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': transaction_id, 
            'message': '交易記錄新增成功',
            'fees_info': fees_info
        }), 201
        
    except Exception as e:
        print(f"新增交易記錄失敗: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """刪除交易記錄"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = 1", (transaction_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': '交易記錄刪除成功'})
        
    except Exception as e:
        print(f"刪除交易記錄失敗: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/brokers', methods=['GET'])
def get_brokers():
    """獲取券商列表"""
    try:
        market = request.args.get('market', 'tw')
        
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cursor.execute("""
            SELECT DISTINCT broker_name, fee_rate, min_fee, discount
            FROM broker_fees
            WHERE market = %s
            ORDER BY broker_name
        """, (market,))
        
        brokers = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'brokers': brokers})
        
    except Exception as e:
        print(f"獲取券商列表失敗: {e}")
        return jsonify({'error': str(e)}), 500
