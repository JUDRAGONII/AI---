"""
台股 API 客戶端（增強版）
資料來源：
- 主要：TWSE OpenAPI、TPEX OpenAPI、TDCC Open Data
- 備援：yfinance (*.TW)、twstock
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import requests
import time

# 添加專案根目錄
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_clients.base_client import BaseAPIClient
from loguru import logger

try:
    import twstock
    TWSTOCK_AVAILABLE = True
except ImportError:
    TWSTOCK_AVAILABLE = False
    logger.warning("twstock 未安裝，將使用備援方案")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance 未安裝")


class TWStockClient(BaseAPIClient):
    """台股資料客戶端（增強版）"""
    
    def __init__(self):
        super().__init__(
            api_name="台股",
            rate_limit_delay=3,  # TWSE API 限流：建議每次請求間隔 3 秒
            daily_limit=None,
            cache_ttl=3600
        )
        
        # TWSE API（證券交易所）
        self.twse_base_url = "https://www.twse.com.tw"
        
        # TPEX API（櫃買中心）
        self.tpex_base_url = "https://www.tpex.org.tw"
        
        # TDCC API（集保結算所）
        self.tdcc_base_url = "https://www.tdcc.com.tw"
    
    def get_stock_list_from_twse(self) -> List[Dict]:
        """
        從 TWSE OpenAPI 取得上市股票清單
        
        Returns:
            股票清單 [{code, name, industry, market}, ...]
        """
        logger.info("從 TWSE OpenAPI 取得上市股票清單...")
        
        try:
            # TWSE 股票清單 API
            url = f"{self.twse_base_url}/rwd/zh/afterTrading/STOCK_DAY_ALL"
            
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                stocks = []
                if 'data' in data:
                    for row in data['data']:
                        # row 格式: [代碼, 名稱, 成交股數, 成交金額, 開盤價, ...]
                        if len(row) >= 2:
                            code = row[0].strip()
                            name = row[1].strip()
                            
                            # 過濾代碼（只要 4 位數字股票）
                            if code.isdigit() and len(code) == 4:
                                stocks.append({
                                    'code': code,
                                    'name': name,
                                    'market': 'TWSE',
                                    'industry': 'Unknown'
                                })
                
                logger.success(f"成功從 TWSE 取得 {len(stocks)} 支上市股票")
                return stocks
            else:
                logger.error(f"TWSE API 回應錯誤: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"從 TWSE 取得股票清單失敗: {e}")
            return []
    
    def get_stock_list_from_tpex(self) -> List[Dict]:
        """
        從 TPEX OpenAPI 取得上櫃股票清單
        
        Returns:
            股票清單 [{code, name, industry, market}, ...]
        """
        logger.info("從 TPEX OpenAPI 取得上櫃股票清單...")
        
        try:
            # TPEX 股票清單 API
            url = f"{self.tpex_base_url}/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php"
            params = {
                'l': 'zh-tw',
                'd': datetime.now().strftime('%Y/%m/%d'),
                'se': 'EW'  # 上櫃股票
            }
            
            response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                stocks = []
                if 'aaData' in data:
                    for row in data['aaData']:
                        # row 格式: [代碼, 名稱, 收盤, 漲跌, ...]
                        if len(row) >= 2:
                            code = row[0].strip()
                            name = row[1].strip()
                            
                            # 過濾代碼
                            if code.isdigit():
                                stocks.append({
                                    'code': code,
                                    'name': name,
                                    'market': 'TPEX',
                                    'industry': 'Unknown'
                                })
                
                logger.success(f"成功從 TPEX 取得 {len(stocks)} 支上櫃股票")
                return stocks
            else:
                logger.error(f"TPEX API 回應錯誤: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"從 TPEX 取得股票清單失敗: {e}")
            return []
    
    def get_stock_list(self, market: str = "ALL") -> List[Dict]:
        """
        取得股票清單（整合所有來源）
        
        Args:
            market: 'TWSE'（上市）、'TPEX'（上櫃）或 'ALL'（全部）
        
        Returns:
            股票清單 [{code, name, industry, market}, ...]
        """
        stocks = []
        
        if market in ["TWSE", "ALL"]:
            # 優先使用 TWSE OpenAPI
            twse_stocks = self.get_stock_list_from_twse()
            if twse_stocks:
                stocks.extend(twse_stocks)
            elif TWSTOCK_AVAILABLE:
                # 備援：使用 twstock
                try:
                    codes = twstock.codes
                    for code, info in codes.items():
                        if info.type == '股票' and info.group != '00':
                            stocks.append({
                                'code': code,
                                'name': info.name,
                                'industry': info.group,
                                'market': 'TWSE'
                            })
                    logger.info(f"使用 twstock 取得 {len(stocks)} 支上市股票（備援）")
                except Exception as e:
                    logger.error(f"twstock 備援失敗: {e}")
        
        if market in ["TPEX", "ALL"]:
            tpex_stocks = self.get_stock_list_from_tpex()
            stocks.extend(tpex_stocks)
        
        return stocks
    
    def get_daily_price_from_twse(
        self,
        stock_code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        從 TWSE OpenAPI 取得日線價格（支援早期資料）
        
        Args:
            stock_code: 股票代碼
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期
        
        Returns:
            DataFrame with columns: trade_date, open, high, low, close, volume
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"從 TWSE OpenAPI 取得 {stock_code} 價格：{start_date} ~ {end_date}")
        
        all_data = []
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # TWSE API 需要逐月查詢
            current = start_dt
            
            while current <= end_dt:
                year = current.year
                month = current.month
                
                # TWSE 日線資料 API
                url = f"{self.twse_base_url}/rwd/zh/afterTrading/STOCK_DAY"
                params = {
                    'date': f"{year}{month:02d}01",
                    'stockNo': stock_code,
                    'response': 'json'
                }
                
                try:
                    response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'data' in data and data['data']:
                            for row in data['data']:
                                # row 格式: [日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, ...]
                                if len(row) >= 7:
                                    try:
                                        # 日期格式：111/01/03（民國年）
                                        date_str = row[0].replace('/', '-')
                                        date_parts = date_str.split('-')
                                        year_ad = int(date_parts[0]) + 1911
                                        trade_date = f"{year_ad}-{date_parts[1]}-{date_parts[2]}"
                                        
                                        all_data.append({
                                            'trade_date': trade_date,
                                            'volume': int(row[1].replace(',', '')) if row[1] != '--' else 0,
                                            'open': float(row[3].replace(',', '')) if row[3] != '--' else None,
                                            'high': float(row[4].replace(',', '')) if row[4] != '--' else None,
                                            'low': float(row[5].replace(',', '')) if row[5] != '--' else None,
                                            'close': float(row[6].replace(',', '')) if row[6] != '--' else None,
                                        })
                                    except (ValueError, IndexError) as e:
                                        continue
                    
                    # 避免過度請求
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.warning(f"取得 {year}/{month} 資料失敗: {e}")
                
                # 移到下個月
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
                df = df.sort_values('trade_date')
                df['adjusted_close'] = df['close']  # 簡化處理
                
                logger.success(f"成功從 TWSE 取得 {len(df)} 筆價格資料")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"從 TWSE 取得價格失敗: {e}")
            return pd.DataFrame()
    
    def get_daily_price(
        self,
        stock_code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        取得股票日線價格（整合所有來源）
        
        優先順序：TWSE OpenAPI -> yfinance -> twstock
        
        Args:
            stock_code: 股票代碼（如 '2330'）
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期，None 表示今天
        
        Returns:
            DataFrame with columns: trade_date, open, high, low, close, volume, adjusted_close
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"取得 {stock_code} 價格資料：{start_date} ~ {end_date}")
        
        # 優先使用 TWSE OpenAPI（支援早期資料）
        df = self.get_daily_price_from_twse(stock_code, start_date, end_date)
        
        if not df.empty:
            return df
        
        # 備援：使用 yfinance
        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(f"{stock_code}.TW")
                hist = ticker.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    # 整理資料格式
                    hist = hist.reset_index()
                    hist.columns = hist.columns.str.lower()
                    hist = hist.rename(columns={'date': 'trade_date'})
                    
                    # 選擇需要的欄位
                    result = hist[['trade_date', 'open', 'high', 'low', 'close', 'volume']].copy()
                    result['trade_date'] = pd.to_datetime(result['trade_date']).dt.date
                    result['adjusted_close'] = hist['close']
                    
                    logger.success(f"成功從 yfinance 取得 {len(result)} 筆價格資料（備援）")
                    return result
                    
            except Exception as e:
                logger.warning(f"yfinance 取得失敗: {e}")
        
        # 最終備援：使用 twstock
        if TWSTOCK_AVAILABLE:
            try:
                stock = twstock.Stock(stock_code)
                
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                
                all_data = []
                current = start_dt
                
                while current <= end_dt:
                    try:
                        data = stock.fetch(current.year, current.month)
                        all_data.extend(data)
                    except:
                        pass
                    
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                
                if all_data:
                    df = pd.DataFrame([{
                        'trade_date': d.date,
                        'open': float(d.open),
                        'high': float(d.high),
                        'low': float(d.low),
                        'close': float(d.close),
                        'volume': int(d.capacity),
                        'adjusted_close': float(d.close)
                    } for d in all_data])
                    
                    df = df[
                        (df['trade_date'] >= start_dt.date()) &
                        (df['trade_date'] <= end_dt.date())
                    ]
                    
                    logger.success(f"成功從 twstock 取得 {len(df)} 筆價格資料（最終備援）")
                    return df
                    
            except Exception as e:
                logger.error(f"twstock 取得失敗: {e}")
        
        logger.error(f"無法從任何來源取得 {stock_code} 的價格資料")
        return pd.DataFrame()
    
    def get_top_stocks(self, n: int = 100) -> List[str]:
        """
        取得市值前 N 大股票代碼
        
        Args:
            n: 數量
        
        Returns:
            股票代碼清單
        """
        # 台股大型權值股（Top 100）
        top_100 = [
            '2330', '2317', '2454', '2308', '2303',  # 台積電、鴻海、聯發科、台達電、聯電
            '2412', '2882', '2881', '2886', '2891',  # 中華電、國泰金、富邦金、兆豐金、中信金
            '2892', '2884', '2885', '2002', '2912',  # 第一金、玉山金、元大金、中鋼、統一超
            '1301', '1303', '1326', '2207', '2382',  # 台塑、南亞、台化、和泰車、廣達
            '3008', '2357', '2379', '2409', '3045',  # 大立光、華碩、瑞昱、友達、台灣大
        ]
        
        return top_100[:n]
    
    def get_shareholder_dispersion_from_tdcc(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        從 TDCC Open Data 取得股權分散表（集保戶股權分散表）
        
        這是計算大戶同步率的唯一權威來源
        
        Args:
            stock_code: 股票代碼
            start_date: 起始日期 'YYYY-MM-DD'（可選）
            end_date: 結束日期（可選）
        
        Returns:
            DataFrame with columns: 
                data_date, stock_code, holders_1_999, holders_1k_5k, ..., 
                total_shareholders, large_holders_percentage, etc.
        """
        logger.info(f"從 TDCC 取得 {stock_code} 股權分散資料...")
        
        try:
            # TDCC Open Data API
            # 股權分散表資料：https://www.tdcc.com.tw/portal/zh/smWeb/qryStock
            # OpenData 下載：https://opendata.twse.com.tw/
            
            # 使用 TWSE OpenData 平台的集保資料
            url = "https://www.tdcc.com.tw/opendata/getOD.ashx"
            params = {
                'id': '1-5'  # 股權分散表
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # TDCC 資料是 CSV 格式
                import io
                
                # 解析 CSV
                df = pd.read_csv(io.StringIO(response.text))
                
                # 欄位名稱可能是中文，需要對應
                # 標準欄位：資料日期、證券代號、證券名稱、各級距人數和股數
                
                # 過濾特定股票
                if '證券代號' in df.columns:
                    df = df[df['證券代號'].astype(str).str.strip() == stock_code]
                
                if df.empty:
                    logger.warning(f"TDCC 無 {stock_code} 的資料")
                    return pd.DataFrame()
                
                # 轉換欄位名稱
                result = self._parse_tdcc_data(df)
                
                # 日期篩選
                if start_date:
                    start_dt = pd.to_datetime(start_date).date()
                    result = result[result['data_date'] >= start_dt]
                
                if end_date:
                    end_dt = pd.to_datetime(end_date).date()
                    result = result[result['data_date'] <= end_dt]
                
                logger.success(f"成功從 TDCC 取得 {len(result)} 筆股權分散資料")
                return result
            else:
                logger.error(f"TDCC API 回應錯誤: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"從 TDCC 取得股權分散資料失敗: {e}")
            return pd.DataFrame()
    
    def _parse_tdcc_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        解析 TDCC 原始資料並計算關鍵指標
        
        Args:
            df: TDCC 原始 DataFrame
        
        Returns:
            格式化後的 DataFrame，包含計算的指標
        """
        result = []
        
        for _, row in df.iterrows():
            try:
                # 解析資料日期（格式可能是 YYYYMMDD 或其他）
                date_str = str(row.get('資料日期', row.get('data_date', '')))
                
                if len(date_str) == 8:  # YYYYMMDD
                    data_date = pd.to_datetime(date_str, format='%Y%m%d').date()
                else:
                    data_date = pd.to_datetime(date_str).date()
                
                stock_code = str(row.get('證券代號', row.get('stock_code', ''))).strip()
                
                # 解析各級距人數（欄位名稱可能略有不同）
                holders_data = {
                    'holders_1_999': self._get_holder_count(row, ['1-999人', '1-999']),
                    'holders_1k_5k': self._get_holder_count(row, ['1,000-5,000人', '1000-5000']),
                    'holders_5k_10k': self._get_holder_count(row, ['5,001-10,000人', '5001-10000']),
                    'holders_10k_15k': self._get_holder_count(row, ['10,001-15,000人', '10001-15000']),
                    'holders_15k_20k': self._get_holder_count(row, ['15,001-20,000人', '15001-20000']),
                    'holders_20k_30k': self._get_holder_count(row, ['20,001-30,000人', '20001-30000']),
                    'holders_30k_40k': self._get_holder_count(row, ['30,001-40,000人', '30001-40000']),
                    'holders_40k_50k': self._get_holder_count(row, ['40,001-50,000人', '40001-50000']),
                    'holders_50k_100k': self._get_holder_count(row, ['50,001-100,000人', '50001-100000']),
                    'holders_100k_200k': self._get_holder_count(row, ['100,001-200,000人', '100001-200000']),
                    'holders_200k_400k': self._get_holder_count(row, ['200,001-400,000人', '200001-400000']),
                    'holders_400k_600k': self._get_holder_count(row, ['400,001-600,000人', '400001-600000']),
                    'holders_600k_800k': self._get_holder_count(row, ['600,001-800,000人', '600001-800000']),
                    'holders_800k_1m': self._get_holder_count(row, ['800,001-1,000,000人', '800001-1000000']),
                    'holders_over_1m': self._get_holder_count(row, ['1,000,001人以上', '1000001以上', '1000001-']),
                }
                
                # 計算總股東人數
                total_shareholders = sum(holders_data.values())
                
                # 計算大戶相關指標
                # 大戶定義：持股 400 張以上（400k 股以上）
                large_holders = (
                    holders_data['holders_400k_600k'] +
                    holders_data['holders_600k_800k'] +
                    holders_data['holders_800k_1m'] +
                    holders_data['holders_over_1m']
                )
                
                large_holders_percentage = (large_holders / total_shareholders * 100) if total_shareholders > 0 else 0
                
                # 計算集中度（前 15% 大股東）
                top15_holders = int(total_shareholders * 0.15)
                concentration_ratio = (large_holders / top15_holders) if top15_holders > 0 else 0
                
                # 組合結果
                record = {
                    'data_date': data_date,
                    'stock_code': stock_code,
                    'total_shareholders': total_shareholders,
                    'large_holders_percentage': round(large_holders_percentage, 4),
                    'concentration_ratio': round(concentration_ratio, 4),
                    **holders_data
                }
                
                result.append(record)
                
            except Exception as e:
                logger.warning(f"解析 TDCC 資料行失敗: {e}")
                continue
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
    
    def _get_holder_count(self, row: pd.Series, possible_columns: List[str]) -> int:
        """
        從多個可能的欄位名稱中提取持有人數
        
        Args:
            row: DataFrame 的一行
            possible_columns: 可能的欄位名稱列表
        
        Returns:
            持有人數（整數）
        """
        for col in possible_columns:
            if col in row.index:
                try:
                    value = row[col]
                    if pd.notna(value):
                        # 移除逗號並轉換為整數
                        return int(str(value).replace(',', '').strip())
                except (ValueError, AttributeError):
                    continue
        return 0
    
    def calculate_synchronization_index(
        self,
        current_data: pd.DataFrame,
        previous_data: pd.DataFrame
    ) -> float:
        """
        計算大戶同步率（核心指標）
        
        同步率 = 大戶增加人數 / (大戶增加人數 + 大戶減少人數)
        
        高同步率（>0.6）表示大戶一致買進，通常是強勢訊號
        低同步率（<0.4）表示大戶分歧，需謹慎
        
        Args:
            current_data: 當期股權分散資料
            previous_data: 前期股權分散資料
        
        Returns:
            同步率（0-1 之間的浮點數）
        """
        try:
            # 大戶級距：400張以上
            large_holder_columns = [
                'holders_400k_600k',
                'holders_600k_800k', 
                'holders_800k_1m',
                'holders_over_1m'
            ]
            
            current_large = sum([current_data.get(col, 0) for col in large_holder_columns])
            previous_large = sum([previous_data.get(col, 0) for col in large_holder_columns])
            
            change = current_large - previous_large
            
            # 同步率計算
            if change > 0:
                # 大戶增加
                sync_index = 0.5 + (change / (2 * abs(change)))  # 趨近 1
            elif change < 0:
                # 大戶減少
                sync_index = 0.5 - (abs(change) / (2 * abs(change)))  # 趨近 0
            else:
                # 無變化
                sync_index = 0.5
            
            return round(max(0, min(1, sync_index)), 4)
            
        except Exception as e:
            logger.error(f"計算同步率失敗: {e}")
            return 0.5


# 使用範例
if __name__ == '__main__':
    client = TWStockClient()
    
    # 測試取得股票清單
    print("\n=== 測試取得股票清單 ===")
    stocks = client.get_stock_list('TWSE')
    print(f"共 {len(stocks)} 支上市股票")
    if stocks:
        print(f"範例: {stocks[0]}")
    
    # 測試取得台積電資料
    print("\n=== 測試取得台積電價格 ===")
    df = client.get_daily_price('2330', '2024-01-01', '2024-01-31')
    print(f"取得 {len(df)} 筆資料")
    if not df.empty:
        print(df.head())
    
    # 測試取得股權分散表（TDCC）
    print("\n=== 測試取得股權分散表 ===")
    dispersion = client.get_shareholder_dispersion_from_tdcc('2330')
    print(f"取得 {len(dispersion)} 筆股權分散資料")
    if not dispersion.empty:
        print(dispersion.head())


