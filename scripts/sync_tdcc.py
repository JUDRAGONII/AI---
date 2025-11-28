"""
TDCC大戶持股數據同步
從TDCC Open API獲取股權分散表
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime, timedelta
from data_loader import DatabaseConnector
from loguru import logger
import time

db = DatabaseConnector()

# TDCC API端點
TDCC_API = "https://www.tdcc.com.tw/opendata/getOD.ashx?id=1-5"

logger.info("=" * 80)
logger.info("📈 同步TDCC大戶持股數據")
logger.info("=" * 80)

try:
    # 獲取TDCC數據
    logger.info("\n📡 從TDCC API獲取數據...")
    
    response = requests.get(TDCC_API, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        logger.info(f"✅ 獲取到 {len(data)} 筆原始數據")
        
        # 只處理前50支股票的最新一筆
        stocks = db.execute_query("SELECT DISTINCT stock_code FROM tw_stock_info ORDER BY stock_code LIMIT 50")
        stock_codes = [s['stock_code'] for s in stocks]
        
        inserted = 0
        for record in data:
            try:
                stock_code = record.get('證券代號', '').strip()
                
                # 只處理我們資料庫中有的股票
                if stock_code not in stock_codes:
                    continue
                
                data_date = record.get('資料日期', '')
                if not data_date:
                    continue
                
                # 轉換日期格式 (假設是20251125格式)
                try:
                    data_date_obj = datetime.strptime(data_date, '%Y%m%d').date()
                except:
                    continue
                
                # 解析持股分級數據
                # 1-999張、1000-5000張、5000-10000張、10000-15000張、15000-20000張、20000-30000張、30000-40000張、40000-50000張、50000-100000張、100000-200000張、200000-400000張、400000-600000張、600000-800000張、800000-1000000張、1000000張以上
                
                holder_1k = int(record.get('持有1-999張人數', 0) or 0)
                shares_1k = int(record.get('持有1-999張股數', 0) or 0)
                
                holder_5k = int(record.get('持有1000-5000張人數', 0) or 0)
                shares_5k = int(record.get('持有1000-5000張股數', 0) or 0)
                
                holder_10k = int(record.get('持有5000-10000張人數', 0) or 0)
                shares_10k = int(record.get('持有5000-10000張股數', 0) or 0)
                
                holder_400k_plus = int(record.get('持有400000張以上人數', 0) or 0)
                shares_400k_plus = int(record.get('持有400000張以上股數', 0) or 0)
                
                # 計算大戶持股比例（400k張以上視為大戶）
                total_shares = int(record.get('總股數', 0) or 0)
                large_holder_ratio = (shares_400k_plus / total_shares * 100) if total_shares > 0 else 0
                
                # 寫入資料庫
                db.execute_query("""
                    INSERT INTO tdcc_shareholder_dispersion 
                    (stock_code, data_date, holder_count_1k, shares_1k, 
                     holder_count_5k, shares_5k, holder_count_10k, shares_10k,
                     holder_count_400k_plus, shares_400k_plus, 
                     total_shares, large_holder_ratio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, data_date) DO UPDATE
                    SET large_holder_ratio = EXCLUDED.large_holder_ratio,
                        total_shares = EXCLUDED.total_shares
                """, (stock_code, data_date_obj, 
                      holder_1k, shares_1k, holder_5k, shares_5k,
                      holder_10k, shares_10k, holder_400k_plus, shares_400k_plus,
                      total_shares, large_holder_ratio))
                
                inserted += 1
                
                if inserted % 10 == 0:
                    logger.info(f"  已處理 {inserted} 支股票...")
                
            except Exception as e:
                logger.error(f"  處理 {stock_code} 失敗: {str(e)[:50]}")
                continue
        
        logger.info(f"\n✅ 成功寫入 {inserted} 筆TDCC數據")
        
        # 顯示示例
        sample = db.execute_query("""
            SELECT stock_code, data_date, large_holder_ratio 
            FROM tdcc_shareholder_dispersion 
            ORDER BY large_holder_ratio DESC 
            LIMIT 5
        """)
        
        logger.info("\n📊 大戶持股比例最高的5支股票:")
        for s in sample:
            logger.info(f"  {s['stock_code']}: {s['large_holder_ratio']:.2f}% ({s['data_date']})")
        
    else:
        logger.error(f"❌ TDCC API請求失敗: HTTP {response.status_code}")
    
    logger.info("\n" + "=" * 80)
    
finally:
    db.close()
