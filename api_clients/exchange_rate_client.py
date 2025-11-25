"""
匯率 API 客戶端
資料來源：ExchangeRate-API
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_clients.base_client import BaseAPIClient
from config.settings import API_KEYS
from loguru import logger


class ExchangeRateClient(BaseAPIClient):
    """匯率資料客戶端"""
    
    def __init__(self):
        super().__init__(
            api_name="匯率",
            api_key=API_KEYS.get('exchange_rate'),
            base_url="https://v6.exchangerate-api.com/v6",
            rate_limit_delay=60,  # 1分鐘
            daily_limit=1500,  # 每月1500次
            cache_ttl=3600
        )
    
    def get_historical_rate(
        self,
        base_currency: str,
        target_currency: str,
        date: str
    ) -> Optional[float]:
        """
        取得特定日期的匯率
        
        Args:
            base_currency: 基準貨幣（如 'USD'）
            target_currency: 目標貨幣（如 'TWD'）
            date: 日期 'YYYY-MM-DD'
        
        Returns:
            匯率
        """
        if not self.api_key:
            logger.error("未設定 ExchangeRate API 金鑰")
            return None
        
        try:
            # 將日期轉換為 YYYY/MM/DD 格式
            dt = datetime.strptime(date, '%Y-%m-%d')
            date_str = dt.strftime('%Y/%m/%d')
            
            url = f"{self.base_url}/{self. api_key}/history/{base_currency}/{date_str}"
            
            data = self.get(url)
            
            if data and 'conversion_rates' in data:
                rate = data['conversion_rates'].get(target_currency)
                if rate:
                    logger.debug(f"{date}: {base_currency}/{target_currency} = {rate}")
                    return float(rate)
                    
        except Exception as e:
            logger.error(f"取得匯率失敗: {e}")
        
        return None
    
    def get_rate_series(
        self,
        base_currency: str,
        target_currency: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        取得一段時間的匯率序列
        
        Args:
            base_currency: 基準貨幣
            target_currency: 目標貨幣
            start_date: 起始日期
            end_date: 結束日期
        
        Returns:
            DataFrame with columns: trade_date, rate
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"取得 {base_currency}/{target_currency} 匯率：{start_date} ~ {end_date}")
        
        # 嘗試使用 yfinance (Yahoo Finance)
        try:
            import yfinance as yf
            
            # yfinance 匯率代碼格式：TWD=X (USD/TWD), EUR=X (USD/EUR)
            # 注意：yfinance 通常是以 USD 為基準
            ticker_symbol = None
            invert = False
            
            if base_currency == 'USD':
                ticker_symbol = f"{target_currency}=X"
            elif target_currency == 'USD':
                ticker_symbol = f"{base_currency}=X"
                invert = True
            
            if ticker_symbol:
                logger.info(f"嘗試使用 yfinance 取得匯率 ({ticker_symbol})...")
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty:
                    df = df.reset_index()
                    df.columns = df.columns.str.lower()
                    df = df.rename(columns={'date': 'trade_date'})
                    
                    result = df[['trade_date', 'close']].copy()
                    result['trade_date'] = pd.to_datetime(result['trade_date']).dt.date
                    result['currency_pair'] = f"{target_currency}/{base_currency}"
                    
                    if invert:
                        result['rate'] = 1 / result['close']
                    else:
                        result['rate'] = result['close']
                        
                    result = result[['trade_date', 'currency_pair', 'rate']]
                    
                    logger.success(f"yfinance 成功取得 {len(result)} 筆匯率資料")
                    return result
                    
        except Exception as e:
            logger.warning(f"yfinance 取得匯率失敗: {e}")
        
        # 備援：ExchangeRate-API
        if not self.api_key:
            logger.error("未設定 ExchangeRate API 金鑰且 yfinance 失敗")
            return pd.DataFrame()
            
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 為節省 API 配額，每週取一次樣本
        current = start_dt
        data_points = []
        
        while current <= end_dt:
            rate = self.get_historical_rate(base_currency, target_currency, current.strftime('%Y-%m-%d'))
            
            if rate:
                data_points.append({
                    'trade_date': current.date(),
                    'currency_pair': f"{target_currency}/{base_currency}",
                    'rate': rate
                })
            
            # 移到下週（節省配額）
            current += timedelta(days=7)
        
        if data_points:
            df = pd.DataFrame(data_points)
            logger.success(f"成功取得 {len(df)} 筆匯率資料")
            return df
        
        return pd.DataFrame()


if __name__ == '__main__':
    client = ExchangeRateClient()
    df = client.get_rate_series('USD', 'TWD', '2024-01-01', '2024-01-31')
    print(df.head())
