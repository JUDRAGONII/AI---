"""
批次同步台股前50大 - 改良版
使用yfinance穩定獲取數據
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime, timedelta
from data_loader import DatabaseConnector
from loguru import logger
import time

# 台股前50大（市值排序）
TOP_50 = [
    '2330', '2317', '2454', '2412', '2882', '2881', '2886', '2308', '2891', '3711',
    '2884', '2912', '2892', '2880', '1301', '1303', '2357', '2382', '2303', '2887',
    '2395', '5880', '6505', '2379', '2474', '3008', '5871', '2408', '3045', '2890',
    '2301', '1216', '2105', '2207', '2609', '2615', '9910', '2888', '1326', '2885',
    '2801', '2883', '2409', '2377', '2327', '3034', '2324', '1402', '2347', '2354'
]

db = DatabaseConnector()
success_stocks = 0
success_prices = 0
failed = []

logger.info("=" * 80)
logger.info(f"🚀 批次同步台股前50大")
logger.info("=" * 80)

try:
    for i, code in enumerate(TOP_50, 1):
        logger.info(f"\n[{i}/50] {code}")
        
        try:
            # 步驟1：寫入股票資訊
            db.bulk_insert('tw_stock_info', [{
                'stock_code': code,
                'stock_name': f'股票{code}',
                'industry': '待更新',
                'market': 'TWSE'
            }])
            success_stocks += 1
            logger.info(f"  ✅ 股票資訊")
            
            # 步驟2：獲取價格（近30天）
            ticker = yf.Ticker(f'{code}.TW')
            df = ticker.history(period='1mo')
            
            if df.empty:
                logger.warning(f"  ⚠️  無價格數據")
                continue
            
            # 寫入價格
            prices = []
            for date, row in df.iterrows():
                prices.append({
                    'stock_code': code,
                    'trade_date': date.date(),
                    'open_price': float(row['Open']),
                    'high_price': float(row['High']),
                    'low_price': float(row['Low']),
                    'close_price': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            count = db.bulk_insert('tw_stock_prices', prices)
            success_prices += count
            logger.info(f"  ✅ 價格: {count}筆")
            
            # 限流
            if i % 10 == 0:
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"  ❌ {str(e)}")
            failed.append(code)
    
    # 統計
    total_stocks = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_info")[0]['c']
    total_prices = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")[0]['c']
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 完成統計")
    logger.info("=" * 80)
    logger.info(f"股票: {total_stocks}支 (新增{success_stocks})")
    logger.info(f"價格: {total_prices}筆 (新增{success_prices})")
    logger.info(f"失敗: {len(failed)}支 {failed if failed else ''}")
    logger.info("=" * 80)
    
finally:
    db.close()
