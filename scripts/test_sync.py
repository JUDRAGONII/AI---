"""
測試腳本 - 同步少量台股數據
只同步前10支台股的股票資訊和近30天價格
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

def test_sync_limited_data():
    """測試同步有限數量的股票數據"""
    
    logger.info("=" * 80)
    logger.info("🧪 開始測試同步（少量數據）")
    logger.info("=" * 80)
    
    client = TWStockClient()
    db = DatabaseConnector()
    
    try:
        # ========== 步驟1：獲取前10支台股 ==========
        logger.info("\n📡 步驟1：獲取台股清單...")
        stocks = client.get_stock_list(market='TWSE')
        
        if not stocks:
            logger.error("❌ 未獲取到股票清單")
            return
        
        # 只取前10支
        test_stocks = stocks[:10]
        logger.info(f"✅ 獲取 {len(test_stocks)} 支測試股票")
        
        for i, stock in enumerate(test_stocks, 1):
            logger.info(f"   {i}. {stock['code']} - {stock['name']}")
        
        # ========== 步驟2：寫入股票資訊 ==========
        logger.info("\n💾 步驟2：寫入股票基本資訊...")
        
        insert_data = []
        for stock in test_stocks:
            insert_data.append({
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'industry': stock.get('industry', '未分類'),
                'market': stock.get('market', 'TWSE'),
                'updated_at': datetime.now()
            })
        
        success_count = db.bulk_insert(
            table='tw_stock_info',
            data=insert_data,
            conflict_action='UPDATE'
        )
        
        logger.info(f"✅ 成功寫入 {success_count} 筆股票資訊")
        
        # ========== 步驟3：回溯價格數據（近30天） ==========
        logger.info("\n📈 步驟3：回溯價格數據（近30天）...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        total_prices = 0
        failed_stocks = []
        
        for i, stock in enumerate(test_stocks, 1):
            stock_code = stock['code']
            logger.info(f"   [{i}/{len(test_stocks)}] 處理 {stock_code} {stock['name']}...")
            
            try:
                # 獲取價格數據
                prices_df = client.get_daily_price(
                    stock_code=stock_code,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                if prices_df.empty:
                    logger.warning(f"      ⚠️  無價格數據")
                    failed_stocks.append(stock_code)
                    continue
                
                # 轉換為字典格式
                price_records = []
                for _, row in prices_df.iterrows():
                    price_records.append({
                        'stock_code': stock_code,
                        'trade_date': row['trade_date'],
                        'open_price': float(row['open']) if 'open' in row else None,
                        'high_price': float(row['high']) if 'high' in row else None,
                        'low_price': float(row['low']) if 'low' in row else None,
                        'close_price': float(row['close']) if 'close' in row else None,
                        'volume': int(row['volume']) if 'volume' in row else 0,
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
                    logger.info(f"      ✅ 寫入 {count} 筆價格")
                
            except Exception as e:
                logger.error(f"      ❌ 失敗: {str(e)}")
                failed_stocks.append(stock_code)
        
        # ========== 步驟4：驗證結果 ==========
        logger.info("\n🔍 步驟4：驗證寫入結果...")
        
        # 檢查股票資訊
        stock_count = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_info")
        stock_total = stock_count[0]['count'] if stock_count else 0
        
        # 檢查價格數據
        price_count = db.execute_query("SELECT COUNT(*) as count FROM tw_stock_prices")
        price_total = price_count[0]['count'] if price_count else 0
        
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
            ORDER BY trade_date DESC 
            LIMIT 5
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
        logger.info(f"  失敗股票: {len(failed_stocks)} 支")
        
        if failed_stocks:
            logger.warning(f"  失敗清單: {', '.join(failed_stocks)}")
        
        logger.info(f"\n範例股票資訊:")
        for stock in sample_stocks:
            logger.info(f"  {stock['stock_code']} {stock['stock_name']} ({stock['industry']})")
        
        logger.info(f"\n範例價格數據:")
        for price in sample_prices:
            logger.info(f"  {price['stock_code']} {price['trade_date']} 收盤:{price['close_price']} 成交量:{price['volume']:,}")
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 測試同步完成！")
        logger.info("=" * 80)
        
        # 測試API
        logger.info("\n🔧 測試API端點...")
        logger.info("可以執行以下命令測試:")
        logger.info(f"  curl http://localhost:5000/api/stocks/list?market=tw&limit=5")
        logger.info(f"  curl http://localhost:5000/api/stocks/{test_stocks[0]['code']}?market=tw")
        logger.info(f"  curl http://localhost:5000/api/prices/{test_stocks[0]['code']}?market=tw&days=7")
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        logger.info("\n✅ 資料庫連接已關閉")


if __name__ == '__main__':
    test_sync_limited_data()
