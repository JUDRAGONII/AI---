"""
綜合數據回補與額度消耗腳本
功能：
1. 回補台股、美股、黃金、匯率的完整歷史數據 (Max History)
2. 對重點資產生成 AI 分析報告以消耗每日剩餘額度
"""
import sys
import os
from pathlib import Path
from loguru import logger
import time
import pandas as pd
import yfinance as yf
from datetime import datetime

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_loader import DatabaseConnector
try:
    from generate_unified_decision import generate_unified_decision_report
except ImportError:
    pass

def fetch_and_save_history(db, symbol, market, is_index=False):
    """抓取完整歷史數據並存入資料庫"""
    try:
        logger.info(f"📥 正在抓取 {symbol} ({market}) 完整歷史數據...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="max")
        
        if df.empty:
            logger.warning(f"⚠️ {symbol} 無數據")
            return False
            
        df = df.reset_index()
        df.columns = df.columns.str.lower()
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'trade_date'})
            
        # 準備數據
        data_list = []
        for _, row in df.iterrows():
            data_list.append({
                'stock_code': symbol,
                'trade_date': row['trade_date'],
                'open_price': row['open'],
                'high_price': row['high'],
                'low_price': row['low'],
                'close_price': row['close'],
                'volume': int(row['volume']),
                # 簡單區分表
                'table': 'us_stock_prices' if market in ['US', 'FOREX', 'COMMODITY'] else 'tw_stock_prices'
            })
            
        # 批量寫入 (使用 UPSERT)
        table_name = 'us_stock_prices' if market in ['US', 'FOREX', 'COMMODITY'] else 'tw_stock_prices'
        
        query = f"""
            INSERT INTO {table_name} 
            (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
            VALUES (%(stock_code)s, %(trade_date)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s, %(volume)s)
            ON CONFLICT (stock_code, trade_date) 
            DO UPDATE SET
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                updated_at = CURRENT_TIMESTAMP
        """
        
        # 分批執行以防內存溢出
        batch_size = 1000
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            db.execute_batch(query, batch)
            
        logger.success(f"✅ {symbol} 歷史數據更新完成 ({len(data_list)} 筆)")
        return True
        
    except Exception as e:
        logger.error(f"❌ {symbol} 處理失敗: {e}")
        return False

def comprehensive_backfill():
    logger.info("🚀 開始執行綜合數據回補與額度消耗任務...")
    db = DatabaseConnector()
    
    try:
        # 1. 定義目標資產清單
        targets = [
            # 黃金與大宗商品
            {'symbol': 'GC=F', 'market': 'COMMODITY', 'name': '黃金期貨'},
            {'symbol': 'GLD', 'market': 'US', 'name': '黃金ETF'},
            {'symbol': 'SI=F', 'market': 'COMMODITY', 'name': '白銀期貨'},
            {'symbol': 'CL=F', 'market': 'COMMODITY', 'name': '原油期貨'},
            
            # 匯率
            {'symbol': 'TWD=X', 'market': 'FOREX', 'name': 'USD/TWD'}, # Yahoo 格式
            {'symbol': 'EUR=X', 'market': 'FOREX', 'name': 'EUR/USD'},
            {'symbol': 'JPY=X', 'market': 'FOREX', 'name': 'USD/JPY'},
            {'symbol': 'DX-Y.NYB', 'market': 'US', 'name': '美元指數'},
            
            # 美股重要 ETF 與個股
            {'symbol': 'QQQ', 'market': 'US', 'name': 'NASDAQ 100'},
            {'symbol': 'SPY', 'market': 'US', 'name': 'S&P 500'},
            {'symbol': 'TLT', 'market': 'US', 'name': '美債20年'},
            {'symbol': 'NVDA', 'market': 'US', 'name': 'NVIDIA'},
            
            # 台股重要權值
            {'symbol': '2330.TW', 'market': 'TW', 'name': '台積電'},
            {'symbol': '2317.TW', 'market': 'TW', 'name': '鴻海'},
            {'symbol': '2454.TW', 'market': 'TW', 'name': '聯發科'},
            {'symbol': '0050.TW', 'market': 'TW', 'name': '元大台灣50'}
        ]
        
        # 2. 數據回補 (Data Backfill)
        for target in targets:
            # 去除 .TW 後綴適配資料庫習慣 (視情況)
            db_symbol = target['symbol'].replace('.TW', '') if target['market'] == 'TW' else target['symbol']
            
            # yfinance 需要 .TW
            yf_symbol = target['symbol']
            
            fetch_and_save_history(db, yf_symbol, target['market'])
            time.sleep(1)

        # 3. AI 報告生成 (Quota Burning)
        logger.info("🔥 開始生成 AI 分析報告以消耗額度...")
        
        # 挑選重點資產進行 AI 分析
        ai_targets = ['GC=F', 'TWD=X', 'NVDA', '2330', '0050']
        
        for code in ai_targets:
            market = 'us'
            if code in ['2330', '0050']:
                market = 'tw'
            # 對於非標準股票代碼 (由 yfinance 處理)，可能需要適配 generate_unified_decision
            # 這裡簡單處理，若失敗則跳過
            
            try:
                # 特別處理 symbol 名稱適配 generate_unified_decision
                clean_code = code.replace('=X', '').replace('=F', '') 
                
                logger.info(f"🤖 Generating AI Report for {code}...")
                
                # 暫時只對股票進行 AI 分析以確保成功
                if code not in ['GC=F', 'TWD=X']:
                    generate_unified_decision_report(stock_code=code, market=market)
                    logger.success(f"✅ AI Report generated for {code}")
                else:
                    logger.info(f"ℹ️ 跳過非股票資產 AI 分析 ({code})，僅回補數據")
                    
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ AI 生成失敗 {code}: {e}")

        logger.info("🏁 綜合回補任務完成！")

    except Exception as e:
        logger.error(f"腳本執行錯誤: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    comprehensive_backfill()
