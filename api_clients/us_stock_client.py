"""
美股 API 客戶端
資料來源：
- 主要：yfinance、Tiingo
- 備援：Alpha Vantage
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
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
    logger.warning("yfinance 未安裝")


class USStockClient(BaseAPIClient):
    """美股資料客戶端"""
    
    def __init__(self):
        super().__init__(
            api_name="美股",
            api_key=API_KEYS.get('tiingo'),
            base_url="https://api.tiingo.com",
            rate_limit_delay=1.0,
            daily_limit=None,
            cache_ttl=3600
        )
        
        self.alpha_vantage_key = API_KEYS.get('alpha_vantage')
    
    def get_sp500_list(self) -> List[str]:
        """
        取得 S&P 500 成分股清單
        
        Returns:
            股票代碼清單
        """
        logger.info("取得 S&P 500 成分股清單...")
        
        # S&P 500 主要成分股（Top 50）
        sp500_top = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',  # 科技巨頭
            'TSLA', 'META', 'BRK.B', 'JPM', 'V',      # Tesla, Meta, 波克夏, 摩根大通, Visa
            'JNJ', 'WMT', 'PG', 'MA', 'UNH',          # 嬌生, 沃爾瑪, 寶僑, Mastercard, 聯合健康
            'HD', 'DIS', 'PYPL', 'BAC', 'ADBE',       # 家得寶, 迪士尼, PayPal, 美銀, Adobe
            'NFLX', 'CMCSA', 'NKE', 'PFE', 'INTC',    # Netflix, Comcast, Nike, 輝瑞, Intel
            'CSCO', 'VZ', 'T', 'MRK', 'PEP',          # Cisco, Verizon, AT&T, 默克, 百事
            'ABT', 'CVX', 'KO', 'NVO', 'TMO',         # 雅培, 雪佛龍, 可口可樂, Novo Nordisk, Thermo Fisher
            'ABBV', 'COST', 'ACN', 'MCD', 'DHR',      # AbbVie, Costco, Accenture, 麥當勞, Danaher
            'LIN', 'AVGO', 'TXN', 'NEE', 'MDT',       # Linde, Broadcom, TI, NextEra, 美敦力
            'UNP', 'PM', 'UPS', 'HON', 'QCOM'         # Union Pacific, 菲利普莫里斯, UPS, 霍尼韋爾, 高通
        ]
        
        logger.success(f"返回 {len(sp500_top)} 支 S&P 500 主要成分股")
        return sp500_top
    
    def get_nasdaq100_list(self) -> List[str]:
        """
        取得 NASDAQ 100 主要成分股清單
        
        Returns:
            股票代碼清單
        """
        logger.info("取得 NASDAQ 100 成分股清單...")
        
        nasdaq100_top = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN',
            'NVDA', 'TSLA', 'META', 'AVGO', 'ASML',
            'PEP', 'COST', 'CSCO', 'ADBE', 'NFLX',
            'CMCSA', 'INTC', 'AMD', 'QCOM', 'TXN',
            'INTU', 'AMGN', 'HON', 'AMAT', 'SBUX',
            'ISRG', 'BKNG', 'ADP', 'GILD', 'VRTX',
            'ADI', 'REGN', 'LRCX', 'PANW', 'MU',
            'MDLZ', 'PYPL', 'SNPS', 'KLAC', 'CDNS',
            'MELI', 'MNST', 'CSX', 'NXPI', 'MRVL',
            'ORLY', 'WDAY', 'FTNT', 'ADSK', 'CHTR'
        ]
        
        logger.success(f"返回 {len(nasdaq100_top)} 支 NASDAQ 100 主要成分股")
        return nasdaq100_top
    
    def get_daily_price(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        取得股票日線價格
        
        Args:
            symbol: 股票代碼（如 'AAPL'）
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期，None 表示今天
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume, adjusted_close
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"取得 {symbol} 價格資料：{start_date} ~ {end_date}")
        
        # 優先使用 yfinance（免費且穩定）
        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty:
                    # 整理格式
                    df = df.reset_index()
                    df.columns = df.columns.str.lower()
                    df = df.rename(columns={'date': 'trade_date'})
                    
                    result = df[['trade_date', 'open', 'high', 'low', 'close', 'volume']].copy()
                    result['trade_date'] = pd.to_datetime(result['trade_date']).dt.date
                    
                    # yfinance 的 Close 已經是調整後價格
                    result['adjusted_close'] = df['close']
                    
                    logger.success(f"成功取得 {len(result)} 筆價格資料（yfinance）")
                    return result
                    
            except Exception as e:
                logger.warning(f"yfinance 取得失敗: {e}，嘗試備援方案")
        
        # 備援：使用 Tiingo
        if self.api_key:
            try:
                url = f"{self.base_url}/tiingo/daily/{symbol}/prices"
                params = {
                    'startDate': start_date,
                    'endDate': end_date,
                    'token': self.api_key
                }
                
                data = self.get(url, params=params)
                
                if data:
                    df = pd.DataFrame(data)
                    df['trade_date'] = pd.to_datetime(df['date']).dt.date
                    
                    result = df[['trade_date', 'open', 'high', 'low', 'close', 'volume']].copy()
                    result['adjusted_close'] = df['adjClose']
                    
                    logger.success(f"成功取得 {len(result)} 筆價格資料（Tiingo）")
                    return result
                    
            except Exception as e:
                logger.error(f"Tiingo 取得失敗: {e}")
        
        # 都失敗，返回空 DataFrame
        logger.error(f"無法取得 {symbol} 的價格資料")
        return pd.DataFrame()
    
    def get_company_info(self, symbol: str) -> Dict:
        """
        取得公司基本資訊
        
        Args:
            symbol: 股票代碼
        
        Returns:
            公司資訊字典
        """
        logger.info(f"取得 {symbol} 公司資訊...")
        
        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'exchange': info.get('exchange', ''),
                    'market_cap': info.get('marketCap', 0)
                }
                
            except Exception as e:
                logger.error(f"取得公司資訊失敗: {e}")
        
        return {}


# 使用範例
if __name__ == '__main__':
    client = USStockClient()
    
    # 測試取得蘋果股價
    df = client.get_daily_price('AAPL', '2024-01-01', '2024-01-31')
    print(df.head())
    
    # 測試取得公司資訊
    info = client.get_company_info('AAPL')
    print(info)
    
    # 測試取得 S&P 500 清單
    sp500 = client.get_sp500_list()
    print(f"S&P 500 成分股: {len(sp500)} 支")
