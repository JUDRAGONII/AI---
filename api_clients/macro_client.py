"""
宏觀經濟資料 API 客戶端
資料來源：FRED API (Federal Reserve Economic Data)
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
    from fredapi import Fred
    FREDAPI_AVAILABLE = True
except ImportError:
    FREDAPI_AVAILABLE = False
    logger.warning("fredapi 未安裝")


class MacroClient(BaseAPIClient):
    """宏觀經濟資料客戶端"""
    
    # FRED 主要經濟指標代碼
    INDICATORS = {
        # 美國指標
        'US_GDP': 'GDP',                      # GDP
        'US_CPI': 'CPIAUCSL',                 # 消費者物價指數
        'US_UNEMPLOYMENT': 'UNRATE',          # 失業率
        'US_INTEREST_RATE': 'FEDFUNDS',       # 聯邦基金利率
        'US_PPI': 'PPIACO',                   # 生產者物價指數
        'US_RETAIL_SALES': 'RSXFS',           # 零售銷售
        
        # 國際指標
        'CHINA_GDP': 'CHNGDPNQDSMEI',         # 中國 GDP
        'EU_GDP': 'CLVMNACSCAB1GQEA19',       # 歐盟 GDP
    }
    
    def __init__(self):
        super().__init__(
            api_name="宏觀經濟",
            api_key=API_KEYS.get('fred'),
            rate_limit_delay=0.5,
            daily_limit=None,
            cache_ttl=86400  # 24小時快取
        )
        
        # 初始化 FRED 客戶端
        if FREDAPI_AVAILABLE and self.api_key:
            self.fred = Fred(api_key=self.api_key)
            logger.info("已初始化 FRED API 客戶端")
        else:
            self.fred = None
            logger.warning("FRED API 未可用")
    
    def get_indicator(
        self,
        indicator_code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        取得經濟指標資料
        
        Args:
            indicator_code: FRED 指標代碼（如 'GDP'）
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期
        
        Returns:
            DataFrame with columns: date, value
        """
        if not self.fred:
            logger.error("FRED API 未初始化")
            return pd.DataFrame()
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"取得經濟指標 {indicator_code}：{start_date} ~ {end_date}")
        
        try:
            # 使用 fredapi 取得資料
            series = self.fred.get_series(
                indicator_code,
                observation_start=start_date,
                observation_end=end_date
            )
            
            if not series.empty:
                df = series.reset_index()
                df.columns = ['date', 'value']
                df['date'] = pd.to_datetime(df['date']).dt.date
                df['indicator_code'] = indicator_code
                
                logger.success(f"成功取得 {len(df)} 筆 {indicator_code} 資料")
                return df
                
        except Exception as e:
            logger.error(f"取得 {indicator_code} 失敗: {e}")
        
        return pd.DataFrame()
    
    def get_multiple_indicators(
        self,
        indicator_codes: List[str],
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        批次取得多個指標
        
        Args:
            indicator_codes: 指標代碼清單
            start_date: 起始日期
           end_date: 結束日期
        
        Returns:
            {indicator_code: DataFrame} 字典
        """
        results = {}
        
        for code in indicator_codes:
            df = self.get_indicator(code, start_date, end_date)
            if not df.empty:
                results[code] = df
        
        logger.info(f"成功取得 {len(results)}/{len(indicator_codes)} 個指標")
        return results
    
    def get_us_core_indicators(
        self,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        取得美國核心經濟指標
        
        Returns:
            包含 GDP、CPI、失業率、利率的字典
        """
        logger.info("取得美國核心經濟指標...")
        
        core_indicators = [
            'GDP',           # GDP
            'CPIAUCSL',      # CPI
            'UNRATE',        # 失業率
            'FEDFUNDS'       # 聯邦基金利率
        ]
        
        return self.get_multiple_indicators(core_indicators, start_date, end_date)


if __name__ == '__main__':
    client = MacroClient()
    
    # 測試取得 GDP
    df = client.get_indicator('GDP', '2020-01-01', '2024-01-01')
    print(df.head())
    
    # 測試取得核心指標
    data = client.get_us_core_indicators('2023-01-01', '2024-01-01')
    for indicator, df in data.items():
        print(f"\n{indicator}:")
        print(df.head())
