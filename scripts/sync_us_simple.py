"""
美股前30支數據同步（簡化穩定版）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
from datetime import datetime, timedelta
from data_loader import DatabaseConnector
from loguru import logger

# 美股前30支（知名度高、數據穩定）
US_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'META', 'TSLA', 'BRK-B', 'JPM', 'JNJ',
    'V', 'WMT', 'PG', 'MA', 'HD',
    'DIS', 'PYPL', 'NFLX', 'ADBE', 'CRM',
    'CMCSA', 'PFE', 'KO', 'PEP', 'COST',
    'TMO', 'ABT', 'MRK', 'CSCO', 'NKE'
]

def sync_us_stocks():
    """同步美股數據"""
    db = DatabaseConnector()
    
    try:
        logger.info("=" * 60)
        logger.info("🇺🇸 開始同步美股前30支")
        logger.info("=" * 60)
        
        stock_count = 0
        price_count = 0
        
        for symbol in US_STOCKS:
            try:
                logger.info(f"處理 {symbol}...")
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 寫入股票資訊
                db.execute_query("""
                    INSERT INTO us_stock_info 
                    (stock_code, stock_name, industry, market)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (stock_code) DO UPDATE
                    SET stock_name = EXCLUDED.stock_name,
                        industry = EXCLUDED.industry
                """, (
                    symbol,
                    info.get('longName', symbol),
                    info.get('industry', ''),
                    'US'
                ))
                stock_count += 1
                
                # 獲取3個月價格數據
                hist = ticker.history(period="3mo")
                
                for date, row in hist.iterrows():
                    try:
                        db.execute_query("""
                            INSERT INTO us_stock_prices 
                            (stock_code, trade_date, close_price, volume)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (stock_code, trade_date) DO UPDATE
                            SET close_price = EXCLUDED.close_price,
                                volume = EXCLUDED.volume
                        """, (
                            symbol,
                            date.date(),
                            float(row['Close']),
                            int(row['Volume'])
                        ))
                        price_count += 1
                    except Exception as e:
                        continue
                
                logger.info(f"  ✅ {symbol} 完成")
                
            except Exception as e:
                logger.error(f"  ❌ {symbol} 失敗: {str(e)[:30]}")
                continue
        
        logger.info("=" * 60)
        logger.info(f"✅ 成功同步 {stock_count} 支美股")
        logger.info(f"✅ 成功寫入 {price_count} 筆價格數據")
        logger.info("=" * 60)
        
        return stock_count
        
    except Exception as e:
        logger.error(f"❌ 同步失敗: {str(e)}")
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    result = sync_us_stocks()
    if result > 0:
        logger.info(f"🎉 美股同步完成！共 {result} 支")
    else:
        logger.error("❌ 美股同步失敗")
