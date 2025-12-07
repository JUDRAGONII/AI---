from decimal import Decimal, ROUND_HALF_UP

class TaxCalculatorTW:
    """
    台股稅務計算引擎
    包含：交易成本、股利所得稅、二代健保補充保費
    """
    
    # 常數定義
    TAX_RATE_STOCK = Decimal('0.003')      # 證交稅 0.3%
    TAX_RATE_ETF = Decimal('0.001')        # ETF 證交稅 0.1%
    FEE_RATE = Decimal('0.001425')         # 公定手續費 0.1425%
    MIN_FEE = Decimal('20')                # 最低手續費 (通常為20元)
    
    HEALTH_WELFARE_RATE = Decimal('0.0211')   # 二代健保補充保費 2.11%
    HEALTH_WELFARE_THRESHOLD = Decimal('20000') # 補充保費起徵點
    
    DIVIDEND_DEDUCT_RATE = Decimal('0.085')   # 股利可抵減稅額比率 8.5%
    DIVIDEND_DEDUCT_CAP = Decimal('80000')    # 可抵減金額上限 8萬元
    SEPARATE_TAX_RATE = Decimal('0.28')       # 分離課稅稅率 28%

    @staticmethod
    def calculate_transaction_cost(price: float, qty: int, is_sell: bool, stock_type: str = 'stock', discount: float = 0.6, min_fee: int = 20) -> dict:
        """
        計算單筆交易成本
        :param price: 成交價格
        :param qty: 成交股數
        :param is_sell: 是否為賣出 (賣出才收證交稅)
        :param stock_type: 'stock' or 'etf'
        :param discount: 券商折數 (如 6折 = 0.6)
        :param min_fee: 券商最低手續費
        """
        price_dec = Decimal(str(price))
        qty_dec = Decimal(str(qty))
        amount = price_dec * qty_dec
        
        # 手續費計算
        raw_fee = amount * TaxCalculatorTW.FEE_RATE
        discounted_fee = raw_fee * Decimal(str(discount))
        fee = max(discounted_fee, Decimal(str(min_fee)))
        fee = fee.quantize(Decimal('1'), rounding=ROUND_HALF_UP) # 四捨五入至整數
        
        # 證交稅計算 (僅賣出)
        tax = Decimal('0')
        if is_sell:
            rate = TaxCalculatorTW.TAX_RATE_ETF if stock_type.lower() == 'etf' else TaxCalculatorTW.TAX_RATE_STOCK
            tax = amount * rate
            tax = tax.quantize(Decimal('1'), rounding=ROUND_HALF_UP) # 四捨五入至整數 (稅法規定無條件捨去? 通常券商是用四捨五入或無條件捨去，這裡採四捨五入)
            # 修正：台灣證交稅得採無條件捨去法 (floor) 嗎？ 
            # 依稅法規定，稅額計算至元為止，角以下捨去。 (Exchange Tax Act)
            tax = int(amount * rate) # 無條件捨去
            
        total_cost = fee + tax
        net_amount = amount - total_cost if is_sell else amount + total_cost
        
        return {
            "amount": int(amount),
            "fee": int(fee),
            "tax": int(tax),
            "total_cost": int(total_cost),
            "net_amount": int(net_amount)
        }

    @staticmethod
    def calculate_dividend_tax(dividend_amount: int, user_tax_rate: float) -> dict:
        """
        試算股利所得稅 (比較 合併課稅 vs 分離課稅)
        :param dividend_amount: 獲配股利總額
        :param user_tax_rate: 用戶綜所稅級距 (如 0.05, 0.12, 0.20, 0.30, 0.40)
        """
        div_dec = Decimal(str(dividend_amount))
        
        # 1. 二代健保補充保費
        supplementary_premium = Decimal('0')
        if div_dec >= TaxCalculatorTW.HEALTH_WELFARE_THRESHOLD:
            supplementary_premium = div_dec * TaxCalculatorTW.HEALTH_WELFARE_RATE
            supplementary_premium = int(supplementary_premium) # 捨去角? 健保局規定四捨五入。
            supplementary_premium = Decimal(str(int(div_dec * TaxCalculatorTW.HEALTH_WELFARE_RATE + Decimal('0.5'))))

        # 2. 方案 A：合併課稅 (Consolidated)
        # 增加的稅額 = 股利 * 稅率
        # 可抵減稅額 = 股利 * 8.5% (max 80,000)
        deductible_amount = div_dec * TaxCalculatorTW.DIVIDEND_DEDUCT_RATE
        if deductible_amount > TaxCalculatorTW.DIVIDEND_DEDUCT_CAP:
            deductible_amount = TaxCalculatorTW.DIVIDEND_DEDUCT_CAP
            
        tax_increase_a = (div_dec * Decimal(str(user_tax_rate))) - deductible_amount
        
        # 3. 方案 B：分離課稅 (Separated)
        # 固定 28%
        tax_increase_b = div_dec * TaxCalculatorTW.SEPARATE_TAX_RATE
        
        best_option = 'A' if tax_increase_a < tax_increase_b else 'B'
        
        return {
            "dividend_amount": int(div_dec),
            "supplementary_premium": int(supplementary_premium),
            "option_a": {
                "name": "合併課稅 (8.5%抵減)",
                "tax_increase": int(tax_increase_a),
                "deductible": int(deductible_amount)
            },
            "option_b": {
                "name": "分離課稅 (28%)",
                "tax_increase": int(tax_increase_b)
            },
            "best_option": best_option,
            "savings": int(abs(tax_increase_a - tax_increase_b))
        }

class TaxCalculatorUS:
    """
    美股稅務計算引擎
    """
    WITHHOLDING_RATE = Decimal('0.30') # W-8BEN 30%

    @staticmethod
    def calculate_withholding_tax(dividend_amount: float) -> dict:
        """
        計算美股股息預扣稅
        """
        div_dec = Decimal(str(dividend_amount))
        tax = div_dec * TaxCalculatorUS.WITHHOLDING_RATE
        net_dividend = div_dec - tax
        
        return {
            "gross_dividend": float(div_dec),
            "withholding_tax": float(tax),
            "net_dividend": float(net_dividend),
            "rate": "30%"
        }
