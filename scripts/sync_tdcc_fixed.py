"""
TDCC數據同步（修正版）- 解決SSL問題
使用verify=False繞過SSL驗證
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime
from data_loader import DatabaseConnector
from loguru import logger

db = DatabaseConnector()

# TDCC API端點
TDCC_API = "https://www.tdcc.com.tw/opendata/getOD.ashx?id=1-5"

logger.info("=" * 80)
logger.info("📈 同步TDCC大戶持股數據（修正版）")
logger.info("=" * 80)

try:
    logger.info("\n📡 從TDCC API獲取數據...")
    
    # 關閉SSL驗證
    response = requests.get(TDCC_API, timeout=30, verify=False)
    
    if response.status_code == 200:
        # 嘗試解析JSON
        try:
            data = response.json()
        except:
            logger.error("❌ 無法解析JSON數據")
            # 嘗試文本格式
            logger.info(f"回應內容（前200字）: {response.text[:200]}")
            data = []
        
        if not data:
            logger.warning("⚠️  TDCC API返回空數據或格式錯誤")
        else:
            logger.info(f"✅ 獲取到 {len(data)} 筆原始數據")
            
            # 只處理前50支股票
            stocks = db.execute_query("SELECT DISTINCT stock_code FROM tw_stock_info ORDER BY stock_code LIMIT 50")
            stock_codes = [s['stock_code'] for s in stocks]
            
            inserted = 0
            for record in data[:100]:  # 只處理前100筆測試
                try:
                    stock_code = record.get('證券代號', '').strip()
                    
                    if stock_code not in stock_codes:
                        continue
                    
                    data_date = record.get('資料日期', '')
                    if not data_date:
                        continue
                    
                    # 轉換日期
                    try:
                        data_date_obj = datetime.strptime(data_date, '%Y%m%d').date()
                    except:
                        continue
                    
                    # 簡化版：只記錄400k以上大戶
                    holder_400k_plus = int(record.get('持有400000張以上人數', 0) or 0)
                    shares_400k_plus = int(record.get('持有400000張以上股數', 0) or 0)
                    total_shares = int(record.get('總股數', 0) or 0)
                    
                    large_holder_ratio = (shares_400k_plus / total_shares * 100) if total_shares > 0 else 0
                    
                    # 寫入
                    db.execute_query("""
                        INSERT INTO tdcc_shareholder_dispersion 
                        (stock_code, data_date, holder_count_400k_plus, 
                         shares_400k_plus, total_shares, large_holder_ratio)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_code, data_date) DO UPDATE
                        SET large_holder_ratio = EXCLUDED.large_holder_ratio
                    """, (stock_code, data_date_obj, holder_400k_plus, 
                          shares_400k_plus, total_shares, large_holder_ratio))
                    
                    inserted += 1
                    
                except Exception as e:
                    continue
            
            logger.info(f"\n✅ 成功寫入 {inserted} 筆TDCC數據")
            
            if inserted > 0:
                # 顯示示例
                sample = db.execute_query("""
                    SELECT stock_code, data_date, large_holder_ratio 
                    FROM tdcc_shareholder_dispersion 
                    ORDER BY large_holder_ratio DESC 
                    LIMIT 5
                """)
                
                logger.info("\n📊 大戶持股比例最高的5支:")
                for s in sample:
                    logger.info(f"  {s['stock_code']}: {s['large_holder_ratio']:.2f}%")
    else:
        logger.error(f"❌ TDCC API請求失敗: HTTP {response.status_code}")
    
    logger.info("\n" + "=" * 80)
    
finally:
    db.close()
