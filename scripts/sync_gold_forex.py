"""
黃金與匯率數據同步
使用yfinance獲取黃金(GC=F)和美元台幣(TWD=X)數據
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime, timedelta
from data_loader import DatabaseConnector
from loguru import logger

db = DatabaseConnector()

logger.info("=" * 80)
logger.info("💰 同步黃金與匯率數據")
logger.info("=" * 80)

try:
    # 黃金數據 (GC=F)
    logger.info("\n📊 同步黃金價格...")
    gold = yf.Ticker("GC=F")
    gold_df = gold.history(period="1y")  # 1年歷史
    
    gold_count = 0
    for date, row in gold_df.iterrows():
        try:
            db.execute_query("""
                INSERT INTO commodity_prices 
                (commodity_code, commodity_name, trade_date, close_price, volume)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (commodity_code, trade_date) DO UPDATE
                SET close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume
            """, ('GOLD', '黃金', date.date(), float(row['Close']), int(row['Volume'])))
            gold_count += 1
        except Exception as e:
            logger.error(f"黃金數據寫入失敗: {str(e)[:50]}")
            break
    
    logger.info(f"✅ 黃金價格: {gold_count}筆")
    
    # 美元台幣匯率 (使用TWD=X)
    logger.info("\n💱 同步美元台幣匯率...")
    
    # 方法1: 嘗試TWD=X
    try:
        usdtwd = yf.Ticker("TWD=X")
        rate_df = usdtwd.history(period="1y")
        
        if rate_df.empty:
            # 方法2: 使用USDTWD=X
            logger.warning("TWD=X無數據，嘗試USDTWD=X...")
            usdtwd = yf.Ticker("USDTWD=X")
            rate_df = usdtwd.history(period="1y")
        
        rate_count = 0
        for date, row in rate_df.iterrows():
            try:
                db.execute_query("""
                    INSERT INTO exchange_rates 
                    (base_currency, quote_currency, trade_date, rate)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (base_currency, quote_currency, trade_date) DO UPDATE
                    SET rate = EXCLUDED.rate
                """, ('USD', 'TWD', date.date(), float(row['Close'])))
                rate_count += 1
            except Exception as e:
                logger.error(f"匯率數據寫入失敗: {str(e)[:50]}")
                break
        
        logger.info(f"✅ 美元台幣匯率: {rate_count}筆")
        
    except Exception as e:
        logger.error(f"匯率數據獲取失敗: {str(e)}")
    
    # 驗證結果
    gold_total = db.execute_query("SELECT COUNT(*) as c FROM commodity_prices WHERE commodity_code='GOLD'")[0]['c']
    rate_total = db.execute_query("SELECT COUNT(*) as c FROM exchange_rates WHERE base_currency='USD' AND quote_currency='TWD'")[0]['c']
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 同步完成統計")
    logger.info("=" * 80)
    logger.info(f"黃金價格總計: {gold_total}筆")
    logger.info(f"匯率總計: {rate_total}筆")
    
    # 顯示最新數據
    latest_gold = db.execute_query("""
        SELECT trade_date, close_price 
        FROM commodity_prices 
        WHERE commodity_code='GOLD' 
        ORDER BY trade_date DESC 
        LIMIT 1
    """, fetch_one=True)
    
    if latest_gold:
        logger.info(f"\n最新黃金價格: ${latest_gold['close_price']:.2f} ({latest_gold['trade_date']})")
    
    latest_rate = db.execute_query("""
        SELECT trade_date, rate 
        FROM exchange_rates 
        WHERE base_currency='USD' AND quote_currency='TWD'
        ORDER BY trade_date DESC 
        LIMIT 1
    """, fetch_one=True)
    
    if latest_rate:
        logger.info(f"最新美元台幣: {latest_rate['rate']:.4f} ({latest_rate['trade_date']})")
    
    logger.info("=" * 80)
    
finally:
    db.close()
