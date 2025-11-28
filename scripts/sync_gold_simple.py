"""
黃金價格數據同步（簡化穩定版）
使用yfinance獲取黃金期貨數據
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime
from data_loader import DatabaseConnector
from loguru import logger

def sync_gold_prices():
    """同步黃金價格數據"""
    db = DatabaseConnector()
    
    try:
        logger.info("=" * 60)
        logger.info("💰 開始同步黃金價格數據")
        logger.info("=" * 60)
        
        # 獲取黃金期貨數據（GC=F）
        logger.info("📡 從yfinance獲取GC=F數據...")
        gold = yf.Ticker("GC=F")
        
        # 獲取1年歷史數據
        gold_df = gold.history(period="1y")
        
        if gold_df.empty:
            logger.error("❌ 無法獲取黃金數據")
            return 0
        
        logger.info(f"✅ 獲取到 {len(gold_df)} 筆黃金數據")
        
        # 批次寫入資料庫
        success_count = 0
        for date, row in gold_df.iterrows():
            try:
                db.execute_query("""
                    INSERT INTO commodity_prices 
                    (commodity_code, commodity_name, trade_date, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (commodity_code, trade_date) 
                    DO UPDATE SET 
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume
                """, (
                    'GOLD',
                    '黃金',
                    date.date(),
                    float(row['Close']),
                    int(row['Volume']) if row['Volume'] > 0 else 0
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"寫入失敗 {date.date()}: {str(e)[:50]}")
                continue
        
        logger.info(f"✅ 成功寫入 {success_count} 筆黃金數據")
        
        # 驗證數據
        total = db.execute_query("""
            SELECT COUNT(*) as count FROM commodity_prices 
            WHERE commodity_code = 'GOLD'
        """, fetch_one=True)
        
        latest = db.execute_query("""
            SELECT trade_date, close_price 
            FROM commodity_prices 
            WHERE commodity_code = 'GOLD'
            ORDER BY trade_date DESC LIMIT 1
        """, fetch_one=True)
        
        logger.info("=" * 60)
        logger.info(f"📊 資料庫總計: {total['count']} 筆黃金數據")
        if latest:
            logger.info(f"💰 最新價格: ${latest['close_price']:.2f} ({latest['trade_date']})")
        logger.info("=" * 60)
        
        return success_count
        
    except Exception as e:
        logger.error(f"❌ 同步失敗: {str(e)}")
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    result = sync_gold_prices()
    if result > 0:
        logger.info(f"🎉 黃金數據同步完成！共 {result} 筆")
    else:
        logger.error("❌ 黃金數據同步失敗")
