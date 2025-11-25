"""資料庫寫入模組"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_CONFIG
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from typing import List, Dict
from loguru import logger


class DatabaseWriter:
    """資料庫寫入類別"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """建立資料庫連線"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
            logger.info("資料庫連線成功")
        except Exception as e:
            logger.error(f"資料庫連線失敗: {e}")
            raise
    
    def close(self):
        """關閉連線"""
        if self.conn:
            self.conn.close()
            logger.info("資料庫連線已關閉")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def insert_tw_stock_prices(self, df: pd.DataFrame) -> int:
        """插入台股價格資料"""
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO tw_stock_prices 
            (stock_code, trade_date, open_price, high_price, low_price, close_price, volume, adjusted_close)
            VALUES %s
            ON CONFLICT (stock_code, trade_date) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                adjusted_close = EXCLUDED.adjusted_close
        """
        
        # 準備資料
        values = [
            (row['stock_code'], row['trade_date'], row['open'], row['high'], 
             row['low'], row['close'], row['volume'], row['adjusted_close'])
            for _, row in df.iterrows()
        ]
       
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆台股價格資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入台股價格失敗: {e}")
            raise
        finally:
            cursor.close()

    def ensure_tw_stock_exists(self, stock_code: str, stock_name: str = 'Unknown'):
        """確保台股基本資料存在"""
        cursor = self.conn.cursor()
        try:
            query = """
                INSERT INTO tw_stock_info (stock_code, stock_name) 
                VALUES (%s, %s) 
                ON CONFLICT (stock_code) DO NOTHING
            """
            cursor.execute(query, (stock_code, stock_name))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"建立台股基本資料失敗: {e}")
        finally:
            cursor.close()

    def ensure_us_stock_exists(self, symbol: str, company_name: str = 'Unknown'):
        """確保美股基本資料存在"""
        cursor = self.conn.cursor()
        try:
            query = """
                INSERT INTO us_stock_info (symbol, company_name) 
                VALUES (%s, %s) 
                ON CONFLICT (symbol) DO NOTHING
            """
            cursor.execute(query, (symbol, company_name))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"建立美股基本資料失敗: {e}")
        finally:
            cursor.close()
    
    def insert_us_stock_prices(self, df: pd.DataFrame) -> int:
        """插入美股價格資料"""
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO us_stock_prices 
            (symbol, trade_date, open_price, high_price, low_price, close_price, volume, adjusted_close)
            VALUES %s
            ON CONFLICT (symbol, trade_date) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                adjusted_close = EXCLUDED.adjusted_close
        """
        
        values = [
            (row['symbol'], row['trade_date'], row['open'], row['high'], 
             row['low'], row['close'], row['volume'], row['adjusted_close'])
            for _, row in df.iterrows()
        ]
        
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆美股價格資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入美股價格失敗: {e}")
            raise
        finally:
            cursor.close()

    def insert_gold_prices(self, df: pd.DataFrame) -> int:
        """插入黃金價格資料"""
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO gold_prices 
            (trade_date, open_price, high_price, low_price, close_price, currency)
            VALUES %s
            ON CONFLICT (trade_date) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                currency = EXCLUDED.currency
        """
        
        values = [
            (row['trade_date'], row['open'], row['high'], 
             row['low'], row['close'], row.get('currency', 'USD'))
            for _, row in df.iterrows()
        ]
        
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆黃金價格資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入黃金價格失敗: {e}")
            raise
        finally:
            cursor.close()

    def insert_exchange_rates(self, df: pd.DataFrame) -> int:
        """插入匯率資料"""
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO exchange_rates 
            (trade_date, currency_pair, rate)
            VALUES %s
            ON CONFLICT (trade_date, currency_pair) DO UPDATE SET
                rate = EXCLUDED.rate
        """
        
        values = [
            (row['trade_date'], row['currency_pair'], row['rate'])
            for _, row in df.iterrows()
        ]
        
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆匯率資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入匯率失敗: {e}")
            raise
        finally:
            cursor.close()
    
    def insert_macro_data(self, df: pd.DataFrame) -> int:
        """插入宏觀經濟資料"""
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO macro_indicators 
            (indicator_type, release_date, value, period, frequency, unit)
            VALUES %s
            ON CONFLICT (indicator_type, release_date) DO UPDATE SET
                value = EXCLUDED.value,
                period = EXCLUDED.period,
                frequency = EXCLUDED.frequency,
                unit = EXCLUDED.unit,
                updated_at = NOW()
        """
        
        values = [
            (row['indicator_type'], row.get('release_date', row.get('date')), row['value'], 
             row.get('period'), row.get('frequency'), row.get('unit'))
            for _, row in df.iterrows()
        ]
        
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆宏觀經濟資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入宏觀經濟資料失敗: {e}")
            raise
        finally:
            cursor.close()

    def insert_financial_news(self, news_list: List[Dict]) -> int:
        """插入金融新聞資料"""
        if not news_list:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO financial_news 
            (source, title, description, url, published_at, author, content, sentiment_score, sentiment_label)
            VALUES %s
            ON CONFLICT (url) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                sentiment_score = EXCLUDED.sentiment_score,
                sentiment_label = EXCLUDED.sentiment_label
        """
        
        values = [
            (news.get('source', 'Unknown'), news['title'], news.get('description'), 
             news['url'], news['published_at'], news.get('author'), 
             news.get('content'), news.get('sentiment_score'), news.get('sentiment_label'))
            for news in news_list
        ]
        
        try:
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 則金融新聞")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入金融新聞失敗: {e}")
            raise
        finally:
            cursor.close()
    
    def update_sync_status(
        self,
        data_source: str,
        source_identifier: str,
        status: str,
        earliest_date=None,
        latest_date=None,
        total_records: int = 0,
        error_message: str = None
    ):
        """更新同步狀態"""
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO sync_status 
            (data_source, source_identifier, sync_status, earliest_date, latest_date, total_records, error_message, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (data_source, source_identifier) DO UPDATE SET
                sync_status = EXCLUDED.sync_status,
        cursor.execute(query, (data_source, source_identifier, status, earliest_date, latest_date, total_records, error_message))
        self.conn.commit()
            插入的筆數
        """
        if df.empty:
            return 0
        
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO shareholder_dispersion (
                stock_code, data_date,
                holders_1_999, holders_1k_5k, holders_5k_10k, holders_10k_15k,
                holders_15k_20k, holders_20k_30k, holders_30k_40k, holders_40k_50k,
                holders_50k_100k, holders_100k_200k, holders_200k_400k, holders_400k_600k,
                holders_600k_800k, holders_800k_1m, holders_over_1m,
                total_shareholders, large_holders_percentage, concentration_ratio,
                synchronization_index, smart_money_flow
            )
            VALUES %s
            ON CONFLICT (stock_code, data_date) DO UPDATE SET
                holders_1_999 = EXCLUDED.holders_1_999,
                holders_1k_5k = EXCLUDED.holders_1k_5k,
                holders_5k_10k = EXCLUDED.holders_5k_10k,
                holders_10k_15k = EXCLUDED.holders_10k_15k,
                holders_15k_20k = EXCLUDED.holders_15k_20k,
                holders_20k_30k = EXCLUDED.holders_20k_30k,
                holders_30k_40k = EXCLUDED.holders_30k_40k,
                holders_40k_50k = EXCLUDED.holders_40k_50k,
                holders_50k_100k = EXCLUDED.holders_50k_100k,
                holders_100k_200k = EXCLUDED.holders_100k_200k,
                holders_200k_400k = EXCLUDED.holders_200k_400k,
                holders_400k_600k = EXCLUDED.holders_400k_600k,
                holders_600k_800k = EXCLUDED.holders_600k_800k,
                holders_800k_1m = EXCLUDED.holders_800k_1m,
                holders_over_1m = EXCLUDED.holders_over_1m,
                total_shareholders = EXCLUDED.total_shareholders,
                large_holders_percentage = EXCLUDED.large_holders_percentage,
                concentration_ratio = EXCLUDED.concentration_ratio,
                synchronization_index = EXCLUDED.synchronization_index,
                smart_money_flow = EXCLUDED.smart_money_flow
        """
        
        try:
            values = []
            for _, row in df.iterrows():
                # 判斷資金流向
                sync_index = row.get('synchronization_index', 0.5)
                if sync_index > 0.6:
                    smart_money_flow = 'INFLOW'
                elif sync_index < 0.4:
                    smart_money_flow = 'OUTFLOW'
                else:
                    smart_money_flow = 'NEUTRAL'
                
                values.append((
                    row['stock_code'],
                    row['data_date'],
                    row.get('holders_1_999', 0),
                    row.get('holders_1k_5k', 0),
                    row.get('holders_5k_10k', 0),
                    row.get('holders_10k_15k', 0),
                    row.get('holders_15k_20k', 0),
                    row.get('holders_20k_30k', 0),
                    row.get('holders_30k_40k', 0),
                    row.get('holders_40k_50k', 0),
                    row.get('holders_50k_100k', 0),
                    row.get('holders_100k_200k', 0),
                    row.get('holders_200k_400k', 0),
                    row.get('holders_400k_600k', 0),
                    row.get('holders_600k_800k', 0),
                    row.get('holders_800k_1m', 0),
                    row.get('holders_over_1m', 0),
                    row.get('total_shareholders', 0),
                    row.get('large_holders_percentage', 0),
                    row.get('concentration_ratio', 0),
                    row.get('synchronization_index', 0.5),
                    smart_money_flow
                ))
            
            execute_values(cursor, query, values)
            self.conn.commit()
            logger.success(f"插入 {len(values)} 筆股權分散資料")
            return len(values)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"插入股權分散資料失敗: {e}")
            raise
        finally:
            cursor.close()
