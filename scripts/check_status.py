import sys
import os
from pathlib import Path
from loguru import logger

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_loader import DatabaseConnector

def check_status():
    print("\n========== 資料庫數據統計 ==========\n")
    try:
        db = DatabaseConnector()
        
        # 1. 檢查台股價格
        tw_count = db.execute_query("SELECT COUNT(*) as c FROM tw_stock_prices")
        tw_last = db.execute_query("SELECT MAX(trade_date) as d FROM tw_stock_prices")
        print(f"📊 台股日線數據: {tw_count[0]['c']:,} 筆 (最新: {tw_last[0]['d']})")
        
        # 2. 檢查美股價格
        us_count = db.execute_query("SELECT COUNT(*) as c FROM us_stock_prices")
        us_last = db.execute_query("SELECT MAX(trade_date) as d FROM us_stock_prices")
        print(f"📊 美股日線數據: {us_count[0]['c']:,} 筆 (最新: {us_last[0]['d']})")
        
        # 3. 檢查 AI 報告
        report_count = db.execute_query("SELECT COUNT(*) as c FROM ai_reports")
        report_last = db.execute_query("SELECT MAX(created_at) as d FROM ai_reports")
        print(f"🤖 AI 分析報告 : {report_count[0]['c']:,} 份 (最新: {report_last[0]['d']})")
        
        # 4. 檢查特別回補資產 (黃金/匯率)
        gold = db.execute_query("SELECT COUNT(*) as c FROM us_stock_prices WHERE stock_code='GC=F'")
        twd = db.execute_query("SELECT COUNT(*) as c FROM us_stock_prices WHERE stock_code='TWD=X'")
        print(f"🌟 黃金期貨 (GC=F): {gold[0]['c']:,} 筆")
        print(f"💱 USD/TWD (TWD=X): {twd[0]['c']:,} 筆")
        
        db.close()
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

    print("\n====================================\n")

if __name__ == '__main__':
    check_status()
