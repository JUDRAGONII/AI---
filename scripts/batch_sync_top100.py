"""
批次同步台股前100大股票
包含股票資訊和近30天價格數據
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api_clients.tw_stock_client import TWStockClient
from data_loader import DatabaseConnector
from loguru import logger

# 台股前100大（市值排序，手動列表）
TOP_100_STOCKS = [
    '2330', '2317', '2454', '2412', '2882', '2881', '2886', '2308', '2891', '3711',
    '2002', '2884', '2912', '2892', '2880', '1301', '1303', '2357', '2382', '2303',
    '2887', '2395', '5880', '6505', '2379', '2474', '3008', '5871', '2408', '3045',
    '2890', '2002', '2301', '1216', '2105', '2207', '2609', '2615', '9910', '2888',
    '1326', '2885', '2801', '2883', '2409', '2377', '2327', '3034', '2324', '1402',
    '2347', '2354', '2049', '2603', '3231', '4904', '2912', '2228', '4938', '2344',
    '2376', '2385', '2371', '1101', '2227', '2313', '2345', '1102', '6669', '2360',
    '3037', '2337', '2352', '2367', '2201', '2356', '2353', '3443', '2388', '2325',
    '6415', '2408', '2384', '1605', '3481', '3661', '2204', '2340', '2022', '3017',
    '6446', '6239', '2923', '3703', '2548', '6176', '4961', '2049', '3035', '1476'
]

def batch_sync_top_stocks():
    """批次同步前100大股票"""
    
    logger.info("=" * 80)
    logger.info("🚀 批次同步台股前100大")
    logger.info("=" * 80)
    
    client = TWStockClient()
    db = DatabaseConnector()
    
    # 去除重複
    stocks_to_sync = list(set(TOP_100_STOCKS))
    logger.info(f"\n📊 準備同步 {len(stocks_to_sync)} 支股票")
    
    total_stocks_success = 0
    total_prices_written = 0
    failed_stocks = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        for i, stock_code in enumerate(stocks_to_sync, 1):
            logger.info(f"\n[{i}/{len(stocks_to_sync)}] 處理 {stock_code}...")
            
            try:
                # 步驟1：寫入股票資訊（基本資料可暫時空白）
                stock_info = {
                    'stock_code': stock_code,
                    'stock_name': f'股票{stock_code}',  # 暫時名稱
                    'industry': '待更新',
                    'market': 'TWSE'
                }
                
                db.bulk_insert(
                    table='tw_stock_info',
                    data=[stock_info],
                    conflict_action='UPDATE'
                )
                logger.info(f"   ✅ 股票資訊已寫入")
                total_stocks_success += 1
                
                # 步驟2：獲取並寫入價格數據
                prices_df = client.get_daily_price(
                    stock_code=stock_code,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                if prices_df is not None and not prices_df.empty:
                    price_records = []
                    for _, row in prices_df.iterrows():
                        price_records.append({
                            'stock_code': stock_code,
                            'trade_date': row['trade_date'],
                            'open_price': float(row['open']) if 'open' in row and row['open'] else None,
                            'high_price': float(row['high']) if 'high' in row and row['high'] else None,
                            'low_price': float(row['low']) if 'low' in row and row['low'] else None,
                            'close_price': float(row['close']) if 'close' in row and row['close'] else None,
                            'volume': int(row['volume']) if 'volume' in row and row['volume'] else 0,
                            'market': 'TW'
                        })
                    
                    if price_records:
                        count = db.bulk_insert(
                            table='tw_stock_prices',
                            data=price_records,
                            conflict_action='UPDATE'
                        )
                        total_prices_written += count
                        logger.info(f"   ✅ 價格數據: {count} 筆")
                else:
                    logger.warning(f"   ⚠️  無價格數據")
                
                # API限流：每10支股票暫停1秒
                if i % 10 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"   ❌ 失敗: {str(e)}")
                failed_stocks.append(stock_code)
        
        # 驗證結果
        stock_count = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_info")[0]['count']
        price_count = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_prices")[0]['count']
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 批次同步完成")
        logger.info("=" * 80)
        logger.info(f"股票資訊: {stock_count} 支（新增 {total_stocks_success}）")
        logger.info(f"價格數據: {price_count} 筆（新增 {total_prices_written}）")
        logger.info(f"失敗: {len(failed_stocks)} 支")
        if failed_stocks:
            logger.warning(f"失敗清單: {', '.join(failed_stocks[:20])}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 批次同步錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        logger.info("\n✅ 完成")

if __name__ == '__main__':
    batch_sync_top_stocks()
