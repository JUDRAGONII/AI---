# ========== 投資組合端點 ==========
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """獲取用戶投資組合"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 獲取持倉數據
        cursor.execute("""
            SELECT 
                up.id,
                up.stock_code,
                up.market,
                up.quantity,
                up.avg_cost,
                up.purchase_date,
                up.notes,
                CASE 
                    WHEN up.market = 'tw' THEN (
                        SELECT close_price 
                        FROM tw_stock_prices 
                        WHERE stock_code = up.stock_code 
                        ORDER BY trade_date DESC 
                        LIMIT 1
                    )
                    WHEN up.market = 'us' THEN (
                        SELECT close_price 
                        FROM us_stock_prices 
                        WHERE stock_code = up.stock_code 
                        ORDER BY trade_date DESC 
                        LIMIT 1
                    )
                END as current_price
            FROM user_portfolios up
            WHERE up.user_id = 1
            ORDER BY up.created_at DESC
        """)
        
        holdings = [dict(row) for row in cursor.fetchall()]
        
        # 計算每個持倉的數據
        total_value = 0
        total_cost = 0
        
        for holding in holdings:
            current_price = float(holding['current_price']) if holding['current_price'] else float(holding['avg_cost'])
            avg_cost = float(holding['avg_cost'])
            quantity = holding['quantity']
            
            market_value = current_price * quantity
            cost_value = avg_cost * quantity
            profit = market_value - cost_value
            profit_rate = (profit / cost_value * 100) if cost_value > 0 else 0
            
            holding['current_price'] = current_price
            holding['market_value'] = round(market_value, 2)
            holding['cost_value'] = round(cost_value, 2)
            holding['profit'] = round(profit, 2)
            holding['profit_rate'] = round(profit_rate, 2)
            holding['purchase_date'] = str(holding['purchase_date'])
            
            total_value += market_value
            total_cost += cost_value
        
        # 計算總損益
        total_profit = total_value - total_cost
        total_return_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        # 計算權重
        for holding in holdings:
            holding['weight'] = round((holding['market_value'] / total_value * 100), 2) if total_value > 0 else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'return_rate': round(total_return_rate, 2),
            'holdings': holdings
        })
        
    except Exception as e:
        print(f"獲取投資組合失敗: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio/holdings', methods=['POST'])
def add_portfolio_holding():
    """新增持倉"""
    try:
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_portfolios 
            (user_id, stock_code, market, quantity, avg_cost, purchase_date, notes)
            VALUES (1, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['stock_code'],
            data['market'],
            data['quantity'],
            data['avg_cost'],
            data.get('purchase_date', datetime.now().date()),
            data.get('notes', '')
        ))
        
        holding_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'id': holding_id, 'message': '持倉新增成功'}), 201
        
    except Exception as e:
        print(f"新增持倉失敗: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio/holdings/<int:holding_id>', methods=['DELETE'])
def delete_portfolio_holding(holding_id):
    """刪除持倉"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM user_portfolios WHERE id = %s AND user_id = 1", (holding_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': '持倉刪除成功'})
        
    except Exception as e:
        print(f"刪除持倉失敗: {e}")
        return jsonify({'error': str(e)}), 500
