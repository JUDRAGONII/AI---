"""
階段4：填充系統元數據
- system_config
- sync_status
- 基礎配置數據
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import DatabaseConnector
from datetime import datetime
from loguru import logger

db = DatabaseConnector()

logger.info("⚙️ 填充系統元數據")

try:
    # 1. 填充system_config（已存在則更新）
    configs = [
        ('max_stocks_per_portfolio', '50', 'number', '每個投資組合最大持股數'),
        ('price_update_frequency', '15', 'number', '價格更新頻率（分鐘）'),
        ('ai_report_cache_days', '7', 'number', 'AI報告快取天數'),
        ('enable_real_time_data', 'false', 'boolean', '啟用即時數據'),
        ('default_market', 'tw', 'string', '預設市場'),
        ('backfill_batch_size', '100', 'number', '回溯批次大小'),
        ('api_rate_limit', '60', 'number', 'API請求限制（每分鐘）'),
    ]
    
    for key, value, type_, desc in configs:
        db.execute_query("""
            INSERT INTO system_config (config_key, config_value, config_type, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (config_key) DO UPDATE
            SET config_value = EXCLUDED.config_value
        """, (key, value, type_, desc))
    
    logger.info(f"✅ system_config: 寫入{len(configs)}筆")
    
    # 2. 填充sync_status
    stocks = db.execute_query("SELECT DISTINCT stock_code FROM tw_stock_prices")
    
    for stock in stocks[:10]:  # 示範記錄前10支
        code = stock['stock_code']
        
        # 獲取日期範圍
        date_range = db.execute_query("""
            SELECT MIN(trade_date) as earliest, MAX(trade_date) as latest, COUNT(*) as cnt
            FROM tw_stock_prices
            WHERE stock_code = %s
        """, (code,), fetch_one=True)
        
        if date_range:
            db.execute_query("""
                INSERT INTO sync_status 
                (data_source, source_identifier, sync_status, earliest_date, latest_date, total_records, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (data_source, source_identifier) DO UPDATE
                SET sync_status = EXCLUDED.sync_status,
                    latest_date = EXCLUDED.latest_date,
                    total_records = EXCLUDED.total_records,
                    updated_at = EXCLUDED.updated_at
            """, ('yfinance', f'TW:{code}', 'completed',
                  date_range['earliest'], date_range['latest'],
                  date_range['cnt'], datetime.now()))
    
    logger.info(f"✅ sync_status: 寫入{min(len(stocks), 10)}筆")
    
    # 3. 驗證
    config_count = db.execute_query("SELECT COUNT(*) as c FROM system_config")[0]['c']
    sync_count = db.execute_query("SELECT COUNT(*) as c FROM sync_status")[0]['c']
    
    logger.info(f"📊 統計:")
    logger.info(f"  system_config: {config_count}筆")
    logger.info(f"  sync_status: {sync_count}筆")
    
finally:
    db.close()
