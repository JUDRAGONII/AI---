"""
全台股上市櫃歷史數據回補腳本
功能：
1. 使用 twstock 獲取所有上市 (tse) 與上櫃 (otc) 股票代碼
2. 自動判斷 yfinance 後綴 (.TW / .TWO)
3. 抓取完整歷史數據 (Max History) 並存入 tw_stock_prices
"""
import sys
import os
from pathlib import Path
from loguru import logger
import time
import pandas as pd
import yfinance as yf
import twstock

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_loader import DatabaseConnector

def fetch_and_save_history(db, symbol):
    """抓取完整歷史數據並存入資料庫"""
    try:
        # logger.info(f"📥 Fetching {symbol}...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="max")
        
        if df.empty:
            # logger.warning(f"⚠️ {symbol} 無數據")
            return False
            
        df = df.reset_index()
        df.columns = df.columns.str.lower()
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'trade_date'})
            
        # 準備數據
        data_list = []
        for _, row in df.iterrows():
            data_list.append({
                'stock_code': symbol.replace('.TW', '').replace('.TWO', ''),
                'trade_date': row['trade_date'],
                'open_price': row['open'],
                'high_price': row['high'],
                'low_price': row['low'],
                'close_price': row['close'],
                'volume': int(row['volume'])
            })
            
        # 批量寫入 (使用 UPSERT)
        query = """
            INSERT INTO tw_stock_prices 
            (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
            VALUES (%(stock_code)s, %(trade_date)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s, %(volume)s)
            ON CONFLICT (stock_code, trade_date) 
            DO UPDATE SET
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                updated_at = CURRENT_TIMESTAMP
        """
        
        # 分批執行以防內存溢出
        batch_size = 2000
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            db.execute_batch(query, batch)
            
        return len(data_list)
        
    except Exception as e:
        logger.error(f"❌ {symbol} 處理失敗: {e}")
        return 0

def backfill_all_tw_stocks():
    logger.info("🚀 開始全台股上市櫃數據回補任務...")
    db = DatabaseConnector()
    
    try:
        # 1. 獲取並分類股票代碼
        codes = twstock.codes
        tse_list = [] # 上市
        otc_list = [] # 上櫃
        
        for code, info in codes.items():
            if info.type == '股票':
                if info.market == '上市':
                    tse_list.append(code)
                elif info.market == '上櫃':
                    otc_list.append(code)
                    
        logger.info(f"📋 發現上市股票: {len(tse_list)} 檔")
        logger.info(f"📋 發現上櫃股票: {len(otc_list)} 檔")
        logger.info(f"📊 總計: {len(tse_list) + len(otc_list)} 檔")
        
        # 2. 執行回補 (先上市後上櫃)
        total_processed = 0
        total_records = 0
        
        all_targets = []
        for c in tse_list:
            all_targets.append({'code': c, 'symbol': f"{c}.TW"})
        for c in otc_list:
            all_targets.append({'code': c, 'symbol': f"{c}.TWO"})
            
        start_time = time.time()
        
        for i, target in enumerate(all_targets):
            symbol = target['symbol']
            
            # 每 50 檔顯示一次進度
            if i % 50 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (i + 1)
                remaining = (len(all_targets) - i) * avg_time
                logger.info(f"🔄 進度: {i}/{len(all_targets)} ({i/len(all_targets)*100:.1f}%) | 預計剩餘時間: {remaining/60:.1f} 分")
            
            count = fetch_and_save_history(db, symbol)
            if count:
                # logger.success(f"✅ {symbol} 更新 {count} 筆")
                total_records += count
                total_processed += 1
            else:
                # logger.warning(f"⚠️ {symbol} 無數據或更新失敗")
                pass
                
            # 輕微限速避免被封 IP
            # time.sleep(0.2) 

        logger.success(f"🏁 全台股回補完成！共處理 {total_processed} 檔股票，寫入 {total_records} 筆數據。")

    except Exception as e:
        logger.error(f"腳本執行錯誤: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    backfill_all_tw_stocks()
