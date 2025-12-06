"""
N8N 自動化腳本 - 每日 AI 報告生成
用於每日市場數據更新後執行 (例如 15:00 for TW, 06:00 for US)
"""
import sys
import os
from pathlib import Path
from loguru import logger
import time
from datetime import datetime

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data_loader import DatabaseConnector
# 嘗試導入報告生成函數
try:
    from generate_unified_decision import generate_unified_decision_report
except ImportError:
    logger.error("❌ 無法導入 generate_unified_decision_report，請確保 generate_unified_decision.py 在專案根目錄")
    sys.exit(1)

def trigger_daily_report(market='TW'):
    """
    觸發 AI 報告生成
    market: 'TW' or 'US'
    """
    logger.info("=" * 60)
    logger.info(f"🚀 [N8N] 開始生成 {market} 市場 AI 報告")
    logger.info("=" * 60)
    
    db = DatabaseConnector()
    
    try:
        # 1. 獲取需要生成報告的股票清單
        # 策略：
        # - 用戶持倉股票 (必須生成)
        # - 用戶關注列表 (可選)
        # - 市場熱門股 (Top 5, 用於展示)
        
        logger.info("🔍 獲取目標股票清單...")
        
        # 持倉
        holdings = db.execute_query(f"""
            SELECT DISTINCT stock_code 
            FROM portfolio_holdings 
            WHERE market = '{market}'
        """)
        
        # 系統核心關注 (Demo用)
        if market == 'TW':
            core_stocks = ['2330', '2317', '2454']
        else:
            core_stocks = ['AAPL', 'NVDA', 'TSLA']
            
        target_codes = set(core_stocks)
        if holdings:
            for h in holdings:
                target_codes.add(h['stock_code'])
        
        logger.info(f"📋 目標股票共 {len(target_codes)} 支")
        
        # 2. 逐一生成報告
        success_count = 0
        error_count = 0
        
        for code in target_codes:
            try:
                logger.info(f"🤖 正在為 {code} 生成 AI 決策報告...")
                
                # 呼叫生成函數
                result = generate_unified_decision_report(stock_code=code, market=market.lower())
                
                if result:
                    logger.success(f"✅ {code} 報告生成成功")
                    success_count += 1
                else:
                    logger.warning(f"⚠️ {code} 報告生成返回空值")
                    error_count += 1
                
                # 避免觸發 API Rate Limit (Gemini Flash 限流較寬鬆但仍要注意)
                time.sleep(3) 
                
            except Exception as e:
                logger.error(f"❌ {code} 生成失敗: {e}")
                error_count += 1
                time.sleep(5) # 失敗後多等待一下
        
        logger.info("=" * 60)
        logger.info("📊 報告生成統計")
        logger.info(f"   目標股票: {len(target_codes)}")
        logger.info(f"   成功生成: {success_count}")
        logger.info(f"   失敗: {error_count}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 腳本執行失敗: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    # 從命令行參數獲取市場，預設 TW
    target_market = 'TW'
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        if arg in ['TW', 'US']:
            target_market = arg
    
    trigger_daily_report(target_market)
