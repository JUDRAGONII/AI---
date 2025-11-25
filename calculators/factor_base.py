"""
量化因子計算器 - 基礎模組
提供所有因子計算的基類和通用工具
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_CONFIG
import psycopg2
from loguru import logger


class FactorCalculatorBase:
    """因子計算器基類"""
    
    def __init__(self):
        """初始化資料庫連接"""
        self.conn = None
        self.connect()
    
    def connect(self):
        """建立資料庫連接"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
            logger.info("因子計算器：資料庫連接成功")
        except Exception as e:
            logger.error(f"因子計算器：資料庫連接失敗 - {e}")
            raise
   
    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_stock_prices(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market: str = 'tw'
    ) -> pd.DataFrame:
        """
        獲取股票價格資料
        
        Args:
            stock_code: 股票代碼
            start_date: 起始日期
            end_date: 結束日期
            market: 'tw' 或 'us'
        
        Returns:
            包含 OHLCV 資料的 DataFrame
        """
        table = 'tw_stock_prices' if market == 'tw' else 'us_stock_prices'
        id_col = 'stock_code' if market == 'tw' else 'symbol'
        
        query = f"""
            SELECT trade_date, open_price, high_price, low_price, 
                   close_price, volume, adjusted_close
            FROM {table}
            WHERE {id_col} = %s 
              AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date
        """
        
        try:
            df = pd.read_sql_query(
                query,
                self.conn,
                params=(stock_code, start_date, end_date)
            )
            
            if df.empty:
                logger.warning(f"無價格資料：{stock_code}")
                return pd.DataFrame()
            
            logger.info(f"獲取 {stock_code} 價格資料：{len(df)} 筆")
            return df
            
        except Exception as e:
            logger.error(f"獲取價格資料失敗：{e}")
            return pd.DataFrame()
    
    def get_fundamental_data(
        self,
        stock_code: str,
        metric: str,
        periods: int = 4
    ) -> pd.DataFrame:
        """
        獲取基本面財務資料
        
        Args:
            stock_code: 股票代碼
            metric: 財務指標（如 'revenue', 'eps', 'roe'）
            periods: 取得最近幾期
        
        Returns:
            財務資料 DataFrame
        """
        query = """
            SELECT report_date, metric, value
            FROM quarterly_fundamentals
            WHERE security_id = (
                SELECT id FROM securities_master WHERE ticker = %s
            )
              AND metric = %s
            ORDER BY report_date DESC
            LIMIT %s
        """
        
        try:
            df = pd.read_sql_query(
                query,
                self.conn,
                params=(stock_code, metric, periods)
            )
            return df
        except Exception as e:
            logger.error(f"獲取基本面資料失敗：{e}")
            return pd.DataFrame()
    
    def calculate_returns(
        self,
        prices: pd.DataFrame,
        period: int = 1
    ) -> pd.Series:
        """
        計算報酬率
        
        Args:
            prices: 價格 DataFrame（須包含 close_price 或 adjusted_close）
            period: 計算期間（天數）
        
        Returns:
            報酬率 Series
        """
        close_col = 'adjusted_close' if 'adjusted_close' in prices.columns else 'close_price'
        
        if close_col not in prices.columns:
            logger.error("價格資料缺少收盤價欄位")
            return pd.Series()
        
        returns = prices[close_col].pct_change(period)
        return returns
    
    def calculate_volatility(
        self,
        prices: pd.DataFrame,
        window: int = 252
    ) -> float:
        """
        計算歷史波動率（年化）
        
        Args:
            prices: 價格 DataFrame
            window: 計算窗口（天數）
        
        Returns:
            年化波動率
        """
        returns = self.calculate_returns(prices, period=1)
        
        if len(returns) < window:
            logger.warning(f"資料不足：需要 {window} 天，僅有 {len(returns)} 天")
            return np.nan
        
        # 年化波動率
        volatility = returns.tail(window).std() * np.sqrt(252)
        return volatility
    
    def calculate_cagr(
        self,
        start_value: float,
        end_value: float,
        periods: int
    ) -> float:
        """
        計算複合年增長率 (CAGR)
        
        Args:
            start_value: 起始值
            end_value: 結束值
            periods: 期數（年）
        
        Returns:
            CAGR
        """
        if start_value <= 0 or end_value <= 0 or periods <= 0:
            return np.nan
        
        cagr = (end_value / start_value) ** (1 / periods) - 1
        return cagr
    
    def normalize_score(
        self,
        value: float,
        lower_bound: float,
        upper_bound: float,
        invert: bool = False
    ) -> float:
        """
        將數值正規化到 0-100 分
        
        Args:
            value: 原始值
            lower_bound: 下界
            upper_bound: 上界
            invert: 是否反轉（值越小分數越高）
        
        Returns:
            0-100 的分數
        """
        if pd.isna(value):
            return 50.0  # 無資料時給予中間分數
        
        # Clip to bounds
        value = max(min(value, upper_bound), lower_bound)
        
        # Normalize to 0-1
        if upper_bound == lower_bound:
            normalized = 0.5
        else:
            normalized = (value - lower_bound) / (upper_bound - lower_bound)
        
        # Invert if needed
        if invert:
            normalized = 1 - normalized
        
        # Scale to 0-100
        score = normalized * 100
        return score


class FactorScoreStorage:
    """因子分數儲存器"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
        except Exception as e:
            logger.error(f"資料庫連接失敗：{e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def save_factor_scores(
        self,
        stock_code: str,
        date: str,
        scores: Dict[str, float],
        market: str = 'tw'
    ):
        """
        儲存因子分數到資料庫
        
        Args:
            stock_code: 股票代碼
            date: 日期
            scores: 因子分數字典 {'value': 75.5, 'quality': 80.0, ...}
            market: 市場
        """
        cursor = self.conn.cursor()
        
        try:
            # 建立或更新 quant_scores 表
            query = """
                INSERT INTO quant_scores (
                    security_id, calculation_date,
                    value_score, quality_score, momentum_score,
                    size_score, volatility_score, growth_score,
                    total_score, created_at
                )
                VALUES (
                    (SELECT id FROM securities_master WHERE ticker = %s),
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
                ON CONFLICT (security_id, calculation_date) 
                DO UPDATE SET
                    value_score = EXCLUDED.value_score,
                    quality_score = EXCLUDED.quality_score,
                    momentum_score = EXCLUDED.momentum_score,
                    size_score = EXCLUDED.size_score,
                    volatility_score = EXCLUDED.volatility_score,
                    growth_score = EXCLUDED.growth_score,
                    total_score = EXCLUDED.total_score,
                    updated_at = NOW()
            """
            
            # 計算總分（可加權）
            total_score = np.mean([
                scores.get('value', 50),
                scores.get('quality', 50),
                scores.get('momentum', 50),
                scores.get('size', 50),
                scores.get('volatility', 50),
                scores.get('growth', 50)
            ])
            
            cursor.execute(query, (
                stock_code,
                date,
                scores.get('value'),
                scores.get('quality'),
                scores.get('momentum'),
                scores.get('size'),
                scores.get('volatility'),
                scores.get('growth'),
                total_score
            ))
            
            self.conn.commit()
            logger.success(f"儲存因子分數：{stock_code} @ {date}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"儲存因子分數失敗：{e}")
        finally:
            cursor.close()
