"""
美元台幣匯率數據同步（簡化穩定版）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime
from data_loader import DatabaseConnector
from loguru import logger

def sync_forex_rates():
    """同步美元台幣匯率"""
    db = DatabaseConnector()
    
    try:
        logger.info("=" * 60)
        logger.info("💱 開始同步美元台幣匯率")
        logger.info("=" * 60)
        
        # 嘗試TWD=X
        logger.info("📡 從yfinance獲取TWD=X數據...")
        ticker = yf.Ticker("TWD=X")
        df = ticker.history(period="1y")
        
        if df.empty:
            logger.warning("TWD=X無數據，嘗試USDTWD=X...")
            ticker = yf.Ticker("USDTWD=X")
            df = ticker.history(period="1y")
        
        if df.empty:
            logger.error("❌ 無法獲取匯率數據")
            return 0
        
        logger.info(f"✅ 獲取到 {len(df)} 筆匯率數據")
        
        # 批次寫入
        success_count = 0
        for date, row in df.iterrows():
            try:
                db.execute_query("""
                    INSERT INTO exchange_rates 
                    (base_currency, quote_currency, trade_date, rate)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (base_currency, quote_currency, trade_date)
                    DO UPDATE SET rate = EXCLUDED.rate
                """, ('USD', 'TWD', date.date(), float(row['Close'])))
                success_count += 1
            except Exception as e:
                logger.error(f"寫入失敗 {date.date()}: {str(e)[:50]}")
                continue
        
        logger.info(f"✅ 成功寫入 {success_count} 筆匯率數據")
        
        # 驗證
        total = db.execute_query("""
            SELECT COUNT(*) as count FROM exchange_rates
            WHERE base_currency = 'USD' AND quote_currency = 'TWD'
        """, fetch_one=True)
        
        latest = db.execute_query("""
            SELECT trade_date, rate FROM exchange_rates
            WHERE base_currency = 'USD' AND quote_currency = 'TWD'
            ORDER BY trade_date DESC LIMIT 1
        """, fetch_one=True)
        
        logger.info("=" * 60)
        logger.info(f"📊 資料庫總計: {total['count']} 筆匯率數據")
        if latest:
            logger.info(f"💱 最新匯率: {latest['rate']:.4f} ({latest['trade_date']})")
        logger.info("=" * 60)
        
        return success_count
        
    except Exception as e:
        logger.error(f"❌ 同步失敗: {str(e)}")
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    result = sync_forex_rates()
    if result > 0:
        logger.info(f"🎉 匯率數據同步完成！共 {result} 筆")
    else:
        logger.error("❌ 匯率數據同步失敗")
