"""
黃金價格 API 客戶端
資料來源：GoldAPI.io、MetalpriceAPI
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_clients.base_client import BaseAPIClient
from config.settings import API_KEYS
from loguru import logger

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class GoldClient(BaseAPIClient):
    """黃金價格客戶端"""
    
    def __init__(self):
        super().__init__(
            api_name="黃金價格",
            api_key=API_KEYS.get('gold_api'),
            base_url="https://www.goldapi.io/api",
            rate_limit_delay=900,  # 15分鐘（免費層限制）
            daily_limit=100,  # 每月100次
            cache_ttl=3600
        )
    
    def get_daily_price(
        self,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        取得黃金日線價格（XAU/USD）
        
        Args:
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期
        
        Returns:
            DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"取得黃金價格：{start_date} ~ {end_date}")
        
        # 使用 yfinance 取得黃金 ETF (GLD) 作為代理
        if YFINANCE_AVAILABLE:
            try:
                # GLD 是最大的黃金 ETF
                ticker = yf.Ticker("GLD")
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty:
                    df = df.reset_index()
                    df.columns = df.columns.str.lower()
                    df = df.rename(columns={'date': 'trade_date'})
                    
                    result = df[['trade_date', 'open', 'high', 'low', 'close']].copy()
                    result['trade_date'] = pd.to_datetime(result['trade_date']).dt.date
                    result['currency'] = 'USD'
                    
                    logger.success(f"成功取得 {len(result)} 筆黃金價格（GLD ETF）")
                    return result
                    
            except Exception as e:
                logger.warning(f"yfinance 取得失敗: {e}")
        
        # 備援：Gold API（注意免費限制）
        if self.api_key:
            try:
                # Gold API 只提供當前價格，歷史資料需要逐日查詢
                logger.warning("Gold API 免費層僅適合即時價格，歷史資料建議使用 yfinance")
                
            except Exception as e:
                logger.error(f"Gold API 失敗: {e}")
        
        return pd.DataFrame()


if __name__ == '__main__':
    client = GoldClient()
    df = client.get_daily_price('2024-01-01', '2024-01-31')
    print(df.head())
