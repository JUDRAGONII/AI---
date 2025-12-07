"""
數據回補腳本
用於消耗剩餘 API 額度，生成更多歷史或冷門股的 AI 報告以充實資料庫
"""
import sys
import os
from pathlib import Path
from loguru import logger
import time
import random

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_loader import DatabaseConnector
from data_loader import DatabaseConnector
from generate_unified_decision import generate_stock_decision_report as generate_unified_decision_report

def fill_quota_backfill():
    logger.info("🚀 開始執行數據回補任務 (消耗剩餘額度)...")
    
    db = DatabaseConnector()
    
    try:
        # 1. 獲取候選股票 (這裡選擇一些非核心但有量的股票)
        # 台股候選
        tw_candidates = [
            '2303', '2603', '2609', '2615', '2891', 
            '2886', '2884', '1301', '1303', '2002',
            '2308', '2382', '2357', '3231', '2371'
        ]
        
        # 美股候選
        us_candidates = [
            'AMD', 'INTC', 'QCOM', 'MU', 'CSCO',
            'NFLX', 'DIS', 'NKE', 'SBUX', 'MCD',
            'JPM', 'BAC', 'WMT', 'COST', 'KO'
        ]
        
        # 混合並隨機打亂
        candidates = []
        for c in tw_candidates:
            candidates.append({'code': c, 'market': 'tw'})
        for c in us_candidates:
            candidates.append({'code': c, 'market': 'us'})
            
        random.shuffle(candidates)
        
        # 2. 檢查已存在的報告，避免重複
        existing = db.execute_query("SELECT stock_code FROM ai_reports WHERE report_type = 'stock_decision'")
        existing_codes = {r['stock_code'] for r in existing}
        
        target_list = [c for c in candidates if c['code'] not in existing_codes]
        
        logger.info(f"📋 預計回補 {len(target_list)} 檔股票的 AI 報告")
        
        # 3. 執行生成 (限制數量以防超時，假設生成 10 檔)
        max_generate = 10
        count = 0
        
        for target in target_list[:max_generate]:
            code = target['code']
            market = target['market']
            
            logger.info(f"Generating report for {code} ({market})...")
            try:
                result = generate_unified_decision_report(stock_code=code, market=market)
                if result:
                    logger.success(f"✅ {code} 生成成功")
                    count += 1
                else:
                    logger.warning(f"⚠️ {code} 生成無結果")
                
                # 休息一下
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ {code} 生成失敗: {e}")
        
        logger.info(f"🏁 回補完成，共生成 {count} 份報告")

    except Exception as e:
        logger.error(f"回補腳本錯誤: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    fill_quota_backfill()
