"""
數據回溯腳本 - 台股股票資訊同步

此腳本會從TWSE/TPEX API獲取股票清單並儲存到資料庫
"""

import sys
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api_clients.tw_stock_client import TWStockClient
from data_loader import DatabaseConnector
from loguru import logger
from datetime import datetime

def sync_tw_stock_info():
    """同步台股股票資訊"""
    
    logger.info("=" * 60)
    logger.info("🚀 開始同步台股股票資訊")
    logger.info("=" * 60)
    
    # 初始化客戶端
    client = TWStockClient()
    db = DatabaseConnector()
    
    try:
        # 1. 獲取股票清單
        logger.info("📡 正在從TWSE/TPEX API獲取股票清單...")
        stocks = client.get_stock_list(market='ALL')
        
        if not stocks:
            logger.error("❌ 未獲取到任何股票資料")
            return
        
        logger.info(f"✅ 成功獲取 {len(stocks)} 支股票")
        
        # 2. 清空現有資料（可選）
        logger.info("🗑️  清空現有tw_stock_info資料...")
        db.execute_query("TRUNCATE TABLE tw_stock_info RESTART IDENTITY CASCADE")
        logger.info("✅ 清空完成")
        
        # 3. 批次插入
        logger.info("💾 開始批次插入資料...")
        
        insert_data = []
        for stock in stocks:
            insert_data.append({
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'industry': stock.get('industry', '未分類'),
                'market': stock.get('market', 'TWSE'),
                'updated_at': datetime.now()
            })
        
        # 使用bulk_insert
        success_count = db.bulk_insert(
            table='tw_stock_info',
            data=insert_data,
            conflict_action='DO NOTHING'
        )
        
        logger.info(f"✅ 成功插入 {success_count} 筆股票資訊")
        
        # 4. 驗證
        result = db.execute_query("SELECT COUNT(*) as total FROM tw_stock_info")
        total = result[0]['total'] if result else 0
        
        logger.info("=" * 60)
        logger.info(f"📊 同步完成統計")
        logger.info("=" * 60)
        logger.info(f"   獲取股票數：{len(stocks)}")
        logger.info(f"   插入成功數：{success_count}")
        logger.info(f"   資料庫總數：{total}")
        logger.info("=" * 60)
        
        # 5. 顯示範例數據
        logger.info("\n📋 範例數據（前5筆）:")
        samples = db.execute_query("""
            SELECT stock_code, stock_name, industry, market 
            FROM tw_stock_info 
            ORDER BY stock_code 
            LIMIT 5
        """)
        
        for i, stock in enumerate(samples, 1):
            logger.info(f"   {i}. {stock['stock_code']} {stock['stock_name']} ({stock['industry']}) - {stock['market']}")
        
        logger.info("\n🎉 台股股票資訊同步完成！")
        
    except Exception as e:
        logger.error(f"❌ 同步失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        logger.info("✅ 資料庫連接已關閉")


if __name__ == '__main__':
    sync_tw_stock_info()
