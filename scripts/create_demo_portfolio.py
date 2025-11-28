"""
創建示範投資組合數據
用於展示投資組合功能
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import DatabaseConnector
from datetime import datetime
from loguru import logger

db = DatabaseConnector()

logger.info("創建示範投資組合")

try:
    # 創建示範用戶投資組合
    portfolios = [
        {'name': '台股成長型', 'total_value': 1000000},
        {'name': '美股科技股', 'total_value': 500000},
        {'name': '穩健收益型', 'total_value': 800000},
    ]
    
    for i, p in enumerate(portfolios, 1):
        db.execute_query("""
            INSERT INTO user_portfolios (user_id, portfolio_name, total_value, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (1, p['name'], p['total_value'], datetime.now(), datetime.now()))
    
    logger.info(f"✅ 創建 {len(portfolios)} 個投資組合")
    
    # 創建示範持倉（台股成長型）
    holdings = [
        {'stock_code': '2330', 'shares': 100, 'avg_price': 500, 'market_value': 50000},
        {'stock_code': '2454', 'shares': 50, 'avg_price': 800, 'market_value': 40000},
        {'stock_code': '2382', 'shares': 80, 'avg_price': 300, 'market_value': 24000},
    ]
    
    for h in holdings:
        db.execute_query("""
            INSERT INTO portfolio_holdings 
            (portfolio_id, stock_code, shares, avg_cost, market_value, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (1, h['stock_code'], h['shares'], h['avg_price'], h['market_value'], datetime.now()))
    
    logger.info(f"✅ 創建 {len(holdings)} 筆持倉")
    
    # 驗證
    p_count = db.execute_query("SELECT COUNT(*) as c FROM user_portfolios")[0]['c']
    h_count = db.execute_query("SELECT COUNT(*) as c FROM portfolio_holdings")[0]['c']
    
    logger.info(f"📊 投資組合: {p_count}個, 持倉: {h_count}筆")
    
finally:
    db.close()
