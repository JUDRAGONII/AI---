"""
進階量化分析 API
提供蒙地卡羅模擬、效率前緣優化與風險分析端點
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from calculators.quant_engine import MonteCarloSimulator, EfficientFrontierOptimizer, RiskFactorAnalyzer
from api_clients.tw_stock_client import TWStockClient
from api_clients.us_stock_client import USStockClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

quant_bp = Blueprint('quant_api', __name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

def fetch_historical_returns(holdings, days=252):
    """
    獲取持倉股票的歷史收益率矩陣
    """
    # 這裡簡化處理：實際應從資料庫查詢
    # 暫時使用 Mock 數據或 API 即時抓取 (如果緩存允許)
    # 為了演示，我們使用 API 客戶端抓取
    
    tw_client = TWStockClient()
    us_client = USStockClient()
    
    all_data = {}
    min_length = float('inf')
    
    # 截止日期
    end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=days*1.5)).strftime('%Y-%m-%d') # 多抓一些確保足夠
    
    for h in holdings:
        code = h['code']
        market = h.get('market', 'TW')
        
        try:
            if market == 'TW':
                df = tw_client.get_daily_price(code, start_date, end_date)
            else:
                df = us_client.get_daily_price(code, start_date, end_date)
                
            if not df.empty:
                # 確保 trade_date 是 datetime
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.set_index('trade_date').sort_index()
                
                # 計算日收益率
                returns = df['close'].pct_change().dropna()
                all_data[code] = returns
                min_length = min(min_length, len(returns))
            else:
                # 如果抓不到，用隨機數據填充 (僅為測試，生產環境應報錯)
                # 實際應該跳過或報錯
                pass
                
        except Exception as e:
            print(f"Error fetching {code}: {e}")
            
    # 對齊數據
    if not all_data:
        return pd.DataFrame()
        
    aligned_data = pd.DataFrame(all_data).dropna()
    return aligned_data

@quant_bp.route('/api/quant/monte-carlo', methods=['POST'])
def run_monte_carlo():
    """
    執行蒙地卡羅模擬
    Body: { 
        "holdings": [{"code": "2330", "weight": 0.4, "market": "TW"}, ...], 
        "simulations": 1000, 
        "days": 252 
    }
    """
    try:
        data = request.json
        holdings = data.get('holdings', [])
        simulations = data.get('simulations', 1000)
        days = data.get('days', 252)
        initial_capital = data.get('initial_capital', 1000000)
        
        if not holdings:
            return jsonify({'success': False, 'error': 'No holdings provided'}), 400
            
        # 準備數據
        returns_df = fetch_historical_returns(holdings)
        
        if returns_df.empty:
            return jsonify({'success': False, 'error': 'Insufficient historical data'}), 400
            
        # 提取權重 - 需要按 returns_df 的列順序排列
        weights_map = {h['code']: h['weight'] for h in holdings}
        ordered_weights = [weights_map.get(col, 0) for col in returns_df.columns]
        
        # 執行模擬
        mc = MonteCarloSimulator(returns_df)
        result = mc.simulate(ordered_weights, num_simulations=simulations, time_horizon=days, initial_capital=initial_capital)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@quant_bp.route('/api/quant/efficient-frontier', methods=['POST'])
def get_efficient_frontier():
    """
    計算效率前緣
    Body: { "holdings": [{"code": "2330", "market": "TW"}, ...] }
    """
    try:
        data = request.json
        holdings = data.get('holdings', [])
        
        if not holdings:
            return jsonify({'success': False, 'error': 'No holdings provided'}), 400
            
        returns_df = fetch_historical_returns(holdings)
        
        if returns_df.empty or len(returns_df.columns) < 2:
            return jsonify({'success': False, 'error': 'Need at least 2 assets with valid data'}), 400
            
        optimizer = EfficientFrontierOptimizer(returns_df)
        result = optimizer.optimize()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@quant_bp.route('/api/quant/risk-analysis', methods=['POST'])
def analyze_risk():
    """
    風險因子分析 (相對於大盤)
    Body: { "code": "2330", "market": "TW", "benchmark": "^TWII" }
    """
    try:
        data = request.json
        code = data.get('code')
        market = data.get('market', 'TW')
        # benchmark = data.get('benchmark') # 暫不支援自訂 benchmark，目前寫死
        
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
            
        # 獲取標的與基準數據
        target_holdings = [{'code': code, 'market': market}]
        benchmark_code = '0050' if market == 'TW' else 'SPY' # 使用 ETF 作為基準代理
        benchmark_holdings = [{'code': benchmark_code, 'market': market}]
        
        target_df = fetch_historical_returns(target_holdings)
        bench_df = fetch_historical_returns(benchmark_holdings)
        
        if target_df.empty or bench_df.empty:
            return jsonify({'success': False, 'error': 'Insufficient data'}), 400
            
        # 執行分析
        target_ret = target_df.iloc[:, 0]
        bench_ret = bench_df.iloc[:, 0]
        
        analyzer = RiskFactorAnalyzer(target_ret, bench_ret)
        result = analyzer.analyze()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
