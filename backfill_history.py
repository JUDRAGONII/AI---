
import yfinance as yf
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

def backfill_stock(stock_code, market, days=365):
    print(f"正在回溯 {stock_code} ({market}) 過去 {days} 天的數據...")
    
    ticker = f"{stock_code}.TW" if market == 'tw' else stock_code
    
    try:
        # 下載數據
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            print(f"⚠️ 無法獲取 {stock_code} 的數據")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        
        table_name = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        count = 0
        
        for index, row in df.iterrows():
            try:
                # 處理 MultiIndex columns (yfinance 新版可能返回 MultiIndex)
                if isinstance(row.index, pd.MultiIndex):
                    open_p = float(row['Open'].iloc[0])
                    high_p = float(row['High'].iloc[0])
                    low_p = float(row['Low'].iloc[0])
                    close_p = float(row['Close'].iloc[0])
                    volume = int(row['Volume'].iloc[0])
                else:
                    # 嘗試直接訪問，若失敗則使用 .item()
                    open_p = float(row['Open']) if not isinstance(row['Open'], pd.Series) else float(row['Open'].iloc[0])
                    high_p = float(row['High']) if not isinstance(row['High'], pd.Series) else float(row['High'].iloc[0])
                    low_p = float(row['Low']) if not isinstance(row['Low'], pd.Series) else float(row['Low'].iloc[0])
                    close_p = float(row['Close']) if not isinstance(row['Close'], pd.Series) else float(row['Close'].iloc[0])
                    volume = int(row['Volume']) if not isinstance(row['Volume'], pd.Series) else int(row['Volume'].iloc[0])

                trade_date = index.date()
                
                cursor.execute(f"""
                    INSERT INTO {table_name} (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, trade_date) 
                    DO UPDATE SET 
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume;
                """, (stock_code, trade_date, open_p, high_p, low_p, close_p, volume))
                count += 1
            except Exception as e:
                print(f"❌ 處理 {trade_date} 數據時出錯: {e}")
                continue
                
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {stock_code} 回溯完成，共更新 {count} 筆數據")
        
    except Exception as e:
        print(f"❌ 下載或寫入 {stock_code} 時發生錯誤: {e}")

if __name__ == "__main__":
    # 定義要回溯的股票清單
    tw_stocks = ['2330', '0050', '2317', '2454', '2603']
    us_stocks = ['AAPL', 'NVDA', 'TSM', 'MSFT', 'GOOGL']
    
    print("="*50)
    print("🚀 開始執行歷史數據回溯 (365天)")
    print("="*50)
    
    for stock in tw_stocks:
        backfill_stock(stock, 'tw')
        
    for stock in us_stocks:
        backfill_stock(stock, 'us')
        
    print("\n✨ 所有回溯任務完成！")
