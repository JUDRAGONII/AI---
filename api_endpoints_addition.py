"""
API Server 新增黃金、匯率、TDCC端點
"""
# 在api_server_v2.py中添加以下端點

@app.route('/api/commodity/<commodity_code>', methods=['GET'])
def get_commodity_prices(commodity_code):
    """獲取商品價格（黃金等）"""
    try:
        days = request.args.get('days', 30, type=int)
        
        prices = db.execute_query("""
            SELECT trade_date, close_price, volume
            FROM commodity_prices
            WHERE commodity_code = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (commodity_code.upper(), days))
        
        return jsonify({
            'commodity': commodity_code,
            'count': len(prices),
            'data': prices
        })
    except Exception as e:
        logger.error(f"❌ 獲取商品價格失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/forex/<pair>', methods=['GET'])
def get_forex_rates(pair):
    """獲取匯率（USD/TWD等）"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # 解析貨幣對 (格式: USDTWD)
        if len(pair) != 6:
            return jsonify({'error': '無效的貨幣對格式，應為XXXYYY'}), 400
        
        base = pair[:3].upper()
        quote = pair[3:].upper()
        
        rates = db.execute_query("""
            SELECT trade_date, rate
            FROM exchange_rates
            WHERE base_currency = %s AND quote_currency = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (base, quote, days))
        
        return jsonify({
            'pair': f'{base}/{quote}',
            'count': len(rates),
            'data': rates
        })
    except Exception as e:
        logger.error(f"❌ 獲取匯率失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tdcc/<stock_code>', methods=['GET'])
def get_tdcc_data_endpoint(stock_code):
    """獲取TDCC大戶持股數據"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        tdcc_data = db.execute_query("""
            SELECT data_date, large_holder_ratio, total_shares,
                   holder_count_400k_plus, shares_400k_plus
            FROM tdcc_shareholder_dispersion
            WHERE stock_code = %s
            ORDER BY data_date DESC
            LIMIT %s
        """, (stock_code, limit))
        
        if not tdcc_data:
            return jsonify({
                'stock_code': stock_code,
                'count': 0,
                'data': [],
                'message': '無TDCC數據'
            })
        
        return jsonify({
            'stock_code': stock_code,
            'count': len(tdcc_data),
            'data': tdcc_data
        })
    except Exception as e:
        logger.error(f"❌ 獲取TDCC數據失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/market/summary', methods=['GET'])
def get_market_summary():
    """獲取市場總覽（黃金、匯率、情緒指標）"""
    try:
        # 最新黃金價格
        gold = db.execute_query("""
            SELECT close_price, trade_date
            FROM commodity_prices
            WHERE commodity_code = 'GOLD'
            ORDER BY trade_date DESC
            LIMIT 1
        """, fetch_one=True)
        
        # 最新美元台幣匯率
        usdtwd = db.execute_query("""
            SELECT rate, trade_date
            FROM exchange_rates
            WHERE base_currency = 'USD' AND quote_currency = 'TWD'
            ORDER BY trade_date DESC
            LIMIT 1
        """, fetch_one=True)
        
        # 台股統計
        tw_stocks = db.execute_query("""
            SELECT COUNT(*) as count FROM tw_stock_info
        """, fetch_one=True)
        
        # 美股統計
        us_stocks = db.execute_query("""
            SELECT COUNT(*) as count FROM us_stock_info
        """, fetch_one=True)
        
        return jsonify({
            'gold': {
                'price': float(gold['close_price']) if gold else None,
                'date': str(gold['trade_date']) if gold else None
            },
            'forex': {
                'usd_twd': float(usdtwd['rate']) if usdtwd else None,
                'date': str(usdtwd['trade_date']) if usdtwd else None
            },
            'stocks': {
                'tw': tw_stocks['count'] if tw_stocks else 0,
                'us': us_stocks['count'] if us_stocks else 0
            }
        })
    except Exception as e:
        logger.error(f"❌ 獲取市場總覽失敗: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 記得在主程式結尾更新端點總數說明
# 新增4個端點: commodity, forex, tdcc, market/summary
# 總計23個端點
