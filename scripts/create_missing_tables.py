"""
創建缺少的資料表
commodity_prices, exchange_rates, market_sentiment
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import DatabaseConnector
from loguru import logger

db = DatabaseConnector()

logger.info("創建缺少的資料表...")

try:
    # 創建commodity_prices表
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS commodity_prices (
            id SERIAL PRIMARY KEY,
            commodity_code VARCHAR(20) NOT NULL,
            commodity_name VARCHAR(100),
            trade_date DATE NOT NULL,
            close_price DECIMAL(15,4),
            open_price DECIMAL(15,4),
            high_price DECIMAL(15,4),
            low_price DECIMAL(15,4),
            volume BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(commodity_code, trade_date)
        )
    """)
    logger.info("✅ commodity_prices表已創建")
    
    # 創建exchange_rates表
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            base_currency VARCHAR(10) NOT NULL,
            quote_currency VARCHAR(10) NOT NULL,
            trade_date DATE NOT NULL,
            rate DECIMAL(15,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(base_currency, quote_currency, trade_date)
        )
    """)
    logger.info("✅ exchange_rates表已創建")
    
    # 創建market_sentiment表（市場情緒指標）
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS market_sentiment (
            id SERIAL PRIMARY KEY,
            indicator_name VARCHAR(100) NOT NULL,
            trade_date DATE NOT NULL,
            value DECIMAL(15,4),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator_name, trade_date)
        )
    """)
    logger.info("✅ market_sentiment表已創建")
    
    # 檢查tdcc_shareholder_dispersion表是否存在
    check = db.execute_query("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='tdcc_shareholder_dispersion'
    """)
    
    if not check:
        db.execute_query("""
            CREATE TABLE tdcc_shareholder_dispersion (
                id SERIAL PRIMARY KEY,
                stock_code VARCHAR(10) NOT NULL,
                data_date DATE NOT NULL,
                holder_count_1k INT,
                shares_1k BIGINT,
                holder_count_5k INT,
                shares_5k BIGINT,
                holder_count_10k INT,
                shares_10k BIGINT,
                holder_count_400k_plus INT,
                shares_400k_plus BIGINT,
                total_shares BIGINT,
                large_holder_ratio DECIMAL(10,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, data_date)
            )
        """)
        logger.info("✅ tdcc_shareholder_dispersion表已創建")
    else:
        logger.info("✅ tdcc_shareholder_dispersion表已存在")
    
    logger.info("\n完成所有表格創建")
    
finally:
    db.close()
