from flask import Blueprint, request, jsonify
from calculators.tax_engine import TaxCalculatorTW, TaxCalculatorUS
import logging

# 定義 Blueprint
tax_api = Blueprint('tax_api', __name__)
logger = logging.getLogger(__name__)

@tax_api.route('/calculate_transaction', methods=['POST'])
def calculate_transaction():
    """
    計算交易成本 API
    Body:
    {
        "market": "tw" or "us",
        "price": float,
        "qty": int,
        "is_sell": bool,
        "stock_type": "stock" or "etf" (tw only),
        "discount": float (broker discount, default 0.6),
        "min_fee": int (default 20)
    }
    """
    try:
        data = request.json
        market = data.get('market', 'tw').lower()
        price = float(data.get('price', 0))
        qty = int(data.get('qty', 0))
        is_sell = bool(data.get('is_sell', False))
        
        if market == 'tw':
            stock_type = data.get('stock_type', 'stock')
            discount = float(data.get('discount', 0.6))
            min_fee = int(data.get('min_fee', 20))
            
            result = TaxCalculatorTW.calculate_transaction_cost(
                price=price, 
                qty=qty, 
                is_sell=is_sell, 
                stock_type=stock_type, 
                discount=discount, 
                min_fee=min_fee
            )
            return jsonify({
                "status": "success",
                "market": "TW",
                "data": result
            })
            
        elif market == 'us':
            # 美股邏輯較簡單，通常免手續費，若有則固定
            commission = float(data.get('commission', 0)) # 美股手續費 (USD)
            amount = price * qty
            total_cost = commission
            net_amount = amount - total_cost if is_sell else amount + total_cost
            
            return jsonify({
                "status": "success",
                "market": "US",
                "data": {
                    "amount": amount,
                    "fee": commission,
                    "tax": 0, # 美股賣出通常無交易稅 (SEC fee 極低可忽略，或後續加上)
                    "total_cost": total_cost,
                    "net_amount": net_amount
                }
            })
            
        else:
            return jsonify({"status": "error", "message": "Unsupported market"}), 400

    except Exception as e:
        logger.error(f"Tax calculation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@tax_api.route('/simulate_dividend', methods=['POST'])
def simulate_dividend():
    """
    股利稅務試算 API
    Body:
    {
        "market": "tw" or "us",
        "amount": float (Total Dividend Amount),
        "tax_rate": float (Individual Income Tax Rate, e.g. 0.05, 0.12, 0.20) - For TW only
    }
    """
    try:
        data = request.json
        market = data.get('market', 'tw').lower()
        amount = float(data.get('amount', 0))
        
        if market == 'tw':
            tax_rate = float(data.get('tax_rate', 0.05)) # 默認 5%
            result = TaxCalculatorTW.calculate_dividend_tax(int(amount), tax_rate)
            return jsonify({
                "status": "success",
                "market": "TW",
                "data": result
            })
            
        elif market == 'us':
            result = TaxCalculatorUS.calculate_withholding_tax(amount)
            return jsonify({
                "status": "success",
                "market": "US",
                "data": result
            })
            
        else:
            return jsonify({"status": "error", "message": "Unsupported market"}), 400

    except Exception as e:
        logger.error(f"Dividend simulation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
