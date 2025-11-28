"""
測試腳本 - 使用手動指定股票清單測試
直接測試幾支知名台股
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api_clients.tw_stock_client import TWStockClient
from data_loader import DatabaseConnector
from loguru import logger

def test_manual_sync():
    """測試手動指定的股票同步"""
    
    logger.info("=" * 80)
    logger.info("🧪 開始測試同步（手動指定股票）")
    logger.info("=" * 80)
    
    # 手動指定測試股票（使用知名大型股）
    test_stocks = [
        {'code': '2330', 'name': '台積電', 'industry': '半導體', 'market': 'TWSE'},
        {'code': '2317', 'name': '鴻海', 'industry': '電子', 'market': 'TWSE'},
        {'code': '2454', 'name': '聯發科', 'industry': '半導體', 'market': 'TWSE'},
        {'code': '2412', 'name': '中華電', 'industry': '電信', 'market': 'TWSE'},
        {'code': '2882', 'name': '國泰金', 'industry': '金融', 'market': 'TWSE'},
    ]
    
    client = TWStockClient()
    db = DatabaseConnector()
    
    try:
        logger.info(f"\n📝 測試股票清單：")
        for i, stock in enumerate(test_stocks, 1):
            logger.info(f"   {i}. {stock['code']} - {stock['name']} ({stock['industry']})")
        
        # ========== 步驟1：寫入股票資訊 ==========
        logger.info("\n💾 步驟1：寫入股票基本資訊...")
        
        insert_data = []
        for stock in test_stocks:
            insert_data.append({
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'industry': stock['industry'],
                'market': stock['market'],
                'updated_at': datetime.now()
            })
        
        success_count = db.bulk_insert(
            table='tw_stock_info',
            data=insert_data,
            conflict_action='UPDATE'
        )
        
        logger.info(f"✅ 成功寫入 {success_count} 筆股票資訊")
        
        # ========== 步驟2：回溯價格數據（近7天測試） ==========
        logger.info("\n📈 步驟2：回溯價格數據（近7天）...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        total_prices = 0
        success_stocks = []
        failed_stocks = []
        
        for i, stock in enumerate(test_stocks, 1):
            stock_code = stock['code']
            logger.info(f"   [{i}/{len(test_stocks)}] 處理 {stock_code} {stock['name']}...")
            
            try:
                # 使用yfinance獲取價格（更穩定）
                prices_df = client.get_daily_price(
                    stock_code=stock_code,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                if prices_df is None or prices_df.empty:
                    logger.warning(f"      ⚠️  無法獲取價格數據")
                    failed_stocks.append(stock_code)
                    continue
                
                logger.info(f"      📊 獲取到 {len(prices_df)} 筆價格")
                
                # 轉換為字典格式
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
                
                # 批次寫入
                if price_records:
                    count = db.bulk_insert(
                        table='tw_stock_prices',
                        data=price_records,
                        conflict_action='UPDATE'
                    )
                    total_prices += count
                    success_stocks.append(stock_code)
                    logger.info(f"      ✅ 寫入 {count} 筆價格")
                
            except Exception as e:
                logger.error(f"      ❌ 失敗: {str(e)}")
                failed_stocks.append(stock_code)
        
        # ========== 步驟3：驗證結果 ==========
        logger.info("\n🔍 步驟3：驗證寫入結果...")
        
        # 檢查股票資訊
        stock_result = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_info")
        stock_total = stock_result[0]['count'] if stock_result else 0
        
        # 檢查價格數據
        price_result = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_prices")
        price_total = price_result[0]['count'] if price_result else 0
        
        # 查看範例數據
        sample_stocks = db.execute_query("""
            SELECT stock_code, stock_name, industry, market 
            FROM tw_stock_info 
            ORDER BY stock_code 
            LIMIT 5
        """)
        
        sample_prices = db.execute_query("""
            SELECT stock_code, trade_date, close_price, volume 
            FROM tw_stock_prices 
            ORDER BY stock_code, trade_date DESC 
            LIMIT 10
        """)
        
        # ========== 結果報告 ==========
        logger.info("\n" + "=" * 80)
        logger.info("📊 測試完成統計")
        logger.info("=" * 80)
        logger.info(f"\n股票資訊:")
        logger.info(f"  目標數量: {len(test_stocks)}")
        logger.info(f"  實際寫入: {success_count}")
        logger.info(f"  資料庫總數: {stock_total}")
        
        logger.info(f"\n價格數據:")
        logger.info(f"  總共寫入: {total_prices} 筆")
        logger.info(f"  資料庫總數: {price_total}")
        logger.info(f"  成功股票: {len(success_stocks)} 支 -> {', '.join(success_stocks)}")
        logger.info(f"  失敗股票: {len(failed_stocks)} 支 -> {', '.join(failed_stocks) if failed_stocks else '無'}")
        
        if sample_stocks:
            logger.info(f"\n✅ 範例股票資訊:")
            for stock in sample_stocks:
                logger.info(f"  {stock['stock_code']} {stock['stock_name']} ({stock['industry']})")
        
        if sample_prices:
            logger.info(f"\n✅ 範例價格數據:")
            for price in sample_prices:
                logger.info(f"  {price['stock_code']} {price['trade_date']} 收盤:{price['close_price']:,.2f} 成交量:{price['volume']:,}")
        
        logger.info("\n" + "=" * 80)
        
        if stock_total > 0 and price_total > 0:
            logger.info("🎉 測試同步成功！")
            logger.info("\n🔧 可以測試以下API端點:")
            logger.info(f"  curl http://localhost:5000/api/stocks/list?market=tw")
            logger.info(f"  curl http://localhost:5000/api/stocks/2330?market=tw")
            logger.info(f"  curl http://localhost:5000/api/prices/2330?market=tw&days=7")
        else:
            logger.warning("⚠️ 測試同步未成功！請檢查錯誤訊息")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        logger.info("\n✅ 資料庫連接已關閉")


if __name__ == '__main__':
    test_manual_sync()
