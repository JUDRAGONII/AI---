# API 使用範例

本文檔提供台股美股金融資料庫系統中所有 API 客戶端的完整使用範例。

## 📚 目錄

- [台股 API (TWStockClient)](#台股-api)
- [美股 API (USStockClient)](#美股-api)
- [黃金價格 API (GoldClient)](#黃金價格-api)
- [匯率 API (ExchangeRateClient)](#匯率-api)
- [宏觀經濟 API (MacroClient)](#宏觀經濟-api)
- [金融新聞 API (NewsClient)](#金融新聞-api)
- [資料庫寫入 (DatabaseWriter)](#資料庫寫入)

---

## 台股 API

### 概述

`TWStockClient` 整合多個台股資料來源：
- **TWSE OpenAPI** (證券交易所官方 API) - 主要來源
- **TPEX OpenAPI** (櫃買中心官方 API) - 上櫃股票
- **TDCC Open Data** (集保結算所) - 股權分散表
- **yfinance** - 備援來源
- **twstock** - 最終備援

### 基本使用

```python
from api_clients.tw_stock_client import TWStockClient

client = TWStockClient()
```

### 1. 取得股票清單

```python
# 取得上市股票清單（從 TWSE OpenAPI）
twse_stocks = client.get_stock_list('TWSE')
print(f"上市股票: {len(twse_stocks)} 支")

# 取得上櫃股票清單（從 TPEX OpenAPI）
tpex_stocks = client.get_stock_list('TPEX')
print(f"上櫃股票: {len(tpex_stocks)} 支")

# 取得全部股票
all_stocks = client.get_stock_list('ALL')
print(f"總計: {len(all_stocks)} 支")

# 股票清單格式
# [{
#     'code': '2330',
#     'name': '台積電',
#     'market': 'TWSE',
#     'industry': '半導體'
# }, ...]
```

### 2. 取得股票價格（歷史資料）

```python
# 取得台積電 1990 年以來的所有資料（TWSE OpenAPI 支援）
df = client.get_daily_price('2330', '1990-01-01', '2024-12-31')

# 資料格式
# trade_date | open | high | low | close | volume | adjusted_close
# 1990-01-02 | 95.0 | 97.0 | 94.5 | 96.0  | 1250000 | 96.0

print(f"取得 {len(df)} 筆歷史資料")
print(df.head())
```

### 3. 股權分散表（TDCC 集保資料）⭐️

**這是計算「大戶同步率」的唯一權威來源**

```python
# 取得台積電股權分散資料
dispersion = client.get_shareholder_dispersion_from_tdcc('2330')

# 資料包含 15 個持股級距
print(f"總股東: {dispersion['total_shareholders'].iloc[-1]}")
print(f"大戶比例: {dispersion['large_holders_percentage'].iloc[-1]:.2f}%")

# 持股級距範例：
# - holders_1_999: 1-999張
# - holders_400k_600k: 40-60萬張 (大戶起點)
# - holders_over_1m: 100萬張以上
```

### 4. 大戶同步率計算

```python
# 計算同步率（核心指標）
if len(dispersion) >= 2:
    current = dispersion.iloc[-1]
    previous = dispersion.iloc[-2]
    
    sync_index = client.calculate_synchronization_index(current, previous)
    
    print(f"同步率: {sync_index:.4f}")
    
    # 判讀
    if sync_index > 0.6:
        print("✅ 高同步率 - 大戶一致買進")
    elif sync_index < 0.4:
        print("⚠️ 低同步率 - 大戶退場")
    else:
        print("➖ 中性 - 大戶分歧")
```

### 完整範例

```python
from api_clients.tw_stock_client import TWStockClient
from data_loader.database_writer import DatabaseWriter

client = TWStockClient()

# 1. 取得價格資料
prices = client.get_daily_price('2330', '2020-01-01', '2024-12-31')

# 2. 取得股權分散（籌碼面）
dispersion = client.get_shareholder_dispersion_from_tdcc('2330')

# 3. 寫入資料庫
with DatabaseWriter() as writer:
    # 確保基本資料存在
    writer.ensure_tw_stock_exists('2330', '台積電')
    
    # 寫入價格
    prices['stock_code'] = '2330'
    writer.insert_tw_stock_prices(prices)
    
    # 寫入股權分散
    writer.insert_shareholder_dispersion(dispersion)
```

---

## 美股 API

### 概述

`USStockClient` 支援多個美股資料來源：
- **yfinance** - 主要來源（免費）
- **Tiingo** - 備援
- **Finnhub** - 實時報價
- **FMP** - 財報資料

### 基本使用

```python
from api_clients.us_stock_client import USStockClient

client = USStockClient()
```

### 1. 取得股票價格

```python
# 取得 Apple 股價（1970年以來）
df = client.get_daily_price('AAPL', '1970-01-01', '2024-12-31')

# 批次取得多支股票
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
for symbol in symbols:
    df = client.get_daily_price(symbol, '2024-01-01')
    print(f"{symbol}: {len(df)} 筆資料")
```

### 2. 取得 S&P 500 清單

```python
# 取得 S&P 500 成分股
sp500 = client.get_sp500_list()
print(f"S&P 500: {len(sp500)} 支股票")

# 格式: ['AAPL', 'MSFT', ...]
```

---

## 黃金價格 API

```python
from api_clients.gold_client import GoldClient

client = GoldClient()

# 取得黃金價格（1968年以來）
df = client.get_gold_prices('1968-01-01', '2024-12-31')

# 資料格式
# trade_date | open | high | low | close | currency
# 1968-01-02 | 35.2 | 35.5 | 35.1 | 35.4  | USD
```

---

## 匯率 API

```python
from api_clients.exchange_rate_client import ExchangeRateClient

client = ExchangeRateClient()

# 取得台幣匯率
df = client.get_exchange_rate('TWD/USD', '1990-01-01', '2024-12-31')

# 支援的貨幣對
pairs = ['TWD/USD', 'EUR/USD', 'GBP/USD', 'JPY/USD', 'CNY/USD']
```

---

## 宏觀經濟 API

### 概述

使用 **FRED API** (美國聯準會經濟資料庫)

### 配置

需要在 `.env` 中設定：
```
FRED_API_KEY=your_fred_api_key
```

### 使用範例

```python
from api_clients.macro_client import MacroClient

client = MacroClient()

# 取得 GDP 資料
gdp = client.get_indicator('GDP', '1960-01-01', '2024-12-31')

# 取得核心經濟指標
core_indicators = client.get_us_core_indicators('2020-01-01')

# 包含：GDP, CPI, 失業率, 利率等
```

---

## 金融新聞 API

### 概述

支援多個新聞來源：
- **Alpha Vantage** - 主要來源
- **Finnhub** - 備援
- **Marketaux** - 備援

### 使用範例

```python
from api_clients.news_client import NewsClient

client = NewsClient()

# 取得最新新聞
news = client.get_latest_news(topics=['technology', 'finance'], limit=50)

# 新聞格式
# [{
#     'source': 'Reuters',
#     'title': '...',
#     'description': '...',
#     'url': 'https://...',
#     'published_at': '2024-11-22 10:30:00',
#     'sentiment_score': 0.75,
#     'sentiment_label': 'positive'
# }, ...]

# 搜尋特定股票新聞
aapl_news = client.search_news('AAPL', days=7)
```

---

## 資料庫寫入

### DatabaseWriter 使用

```python
from data_loader.database_writer import DatabaseWriter

with DatabaseWriter() as writer:
    # 1. 台股價格
    writer.ensure_tw_stock_exists('2330', '台積電')
    writer.insert_tw_stock_prices(tw_price_df)
    
    # 2. 美股價格
    writer.ensure_us_stock_exists('AAPL', 'Apple Inc.')
    writer.insert_us_stock_prices(us_price_df)
    
    # 3. 黃金價格
    writer.insert_gold_prices(gold_df)
    
    # 4. 匯率
    writer.insert_exchange_rates(rate_df)
    
    # 5. 宏觀經濟
    writer.insert_macro_data(macro_df)
    
    # 6. 金融新聞
    writer.insert_financial_news(news_list)
    
    # 7. 股權分散（TDCC）⭐️
    writer.insert_shareholder_dispersion(dispersion_df)
    
    # 8. 更新同步狀態
    writer.update_sync_status(
        data_source='tw_stock',
        source_identifier='2330',
        status='success',
        total_records=len(tw_price_df)
    )
```

---

## 完整資料回溯範例

```python
from datetime import datetime
from api_clients.tw_stock_client import TWStockClient
from api_clients.us_stock_client import USStockClient
from api_clients.gold_client import GoldClient
from data_loader.database_writer import DatabaseWriter

def backfill_all_data():
    """完整資料回溯範例"""
    
    # 設定日期範圍
    start_date = '1990-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    with DatabaseWriter() as writer:
        # === Phase 1: 基礎資料 ===
        print("Phase 1: 黃金與匯率")
        
        gold_client = GoldClient()
        gold_df = gold_client.get_gold_prices(start_date, end_date)
        writer.insert_gold_prices(gold_df)
        
        # === Phase 2: 台股 ===
        print("Phase 2: 台股資料")
        
        tw_client = TWStockClient()
        top_stocks = tw_client.get_top_stocks(25)  # Top 25
        
        for stock_code in top_stocks:
            print(f"處理 {stock_code}...")
            
            # 價格資料
            prices = tw_client.get_daily_price(stock_code, start_date, end_date)
            if not prices.empty:
                writer.ensure_tw_stock_exists(stock_code)
                prices['stock_code'] = stock_code
                writer.insert_tw_stock_prices(prices)
            
            # 股權分散（籌碼）
            dispersion = tw_client.get_shareholder_dispersion_from_tdcc(stock_code)
            if not dispersion.empty:
                writer.insert_shareholder_dispersion(dispersion)
        
        # === Phase 3: 美股 ===
        print("Phase 3: 美股資料")
        
        us_client = USStockClient()
        us_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in us_symbols:
            prices = us_client.get_daily_price(symbol, start_date, end_date)
            if not prices.empty:
                writer.ensure_us_stock_exists(symbol)
                prices['symbol'] = symbol
                writer.insert_us_stock_prices(prices)

if __name__ == '__main__':
    backfill_all_data()
```

---

## API 設定與配置

### 環境變數 (.env)

```bash
# FRED API (宏觀經濟) - 必須
FRED_API_KEY=your_fred_api_key

# Alpha Vantage (新聞、股票) - 必須
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Tiingo (美股備援) - 可選
TIINGO_API_KEY=your_tiingo_key

# Finnhub (股票、新聞) - 可選
FINNHUB_API_KEY=your_finnhub_key

# FMP (財報資料) - 可選
FMP_API_KEY=your_fmp_key
```

### API 申請連結

| API | 申請網址 | 免費額度 |
|-----|---------|---------|
| FRED | https://fred.stlouisfed.org/docs/api/api_key.html | 無限制 |
| Alpha Vantage | https://www.alphavantage.co/support/#api-key | 500 calls/day |
| Tiingo | https://www.tiingo.com/ | 500 calls/hour |
| Finnhub | https://finnhub.io/ | 60 calls/min |
| FMP | https://financialmodelingprep.com/developer/docs/ | 250 calls/day |

---

## 常見問題

### Q: 如何避免 API 限流？

```python
# 使用 rate_limit_delay 參數
client = TWStockClient()
# 已內建限流保護（每次請求間隔 3 秒）
```

### Q: 如何處理資料缺失？

```python
# 檢查 DataFrame 是否為空
df = client.get_daily_price('2330', '1990-01-01')

if df.empty:
    print("無資料")
else:
    print(f"成功取得 {len(df)} 筆資料")
```

### Q: 如何更新已存在的資料？

```python
# DatabaseWriter 使用 ON CONFLICT DO UPDATE
# 重複資料會自動更新而不是插入
writer.insert_tw_stock_prices(df)  # 自動處理衝突
```

---

## 進階功能

### 1. 並行處理

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_stock(stock_code):
    client = TWStockClient()
    return client.get_daily_price(stock_code, '2024-01-01')

stocks = ['2330', '2317', '2454', '2308']

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(fetch_stock, stocks))
```

### 2. 錯誤處理

```python
from loguru import logger

try:
    df = client.get_daily_price('2330', '1990-01-01')
except Exception as e:
    logger.error(f"取得資料失敗: {e}")
    df = pd.DataFrame()  # 返回空 DataFrame
```

### 3. 資料驗證

```python
def validate_price_data(df):
    """驗證價格資料完整性"""
    required_columns = ['trade_date', 'open', 'high', 'low', 'close', 'volume']
    
    if not all(col in df.columns for col in required_columns):
        raise ValueError("資料欄位不完整")
    
    if df['high'].min() < df['low'].max():
        logger.warning("發現異常價格資料")
    
    return True
```

---

## 貢獻指南

如需添加新的 API 客戶端：

1. 繼承 `BaseAPIClient`
2. 實作 `get()` 和 `post()` 方法
3. 添加限流保護
4. 編寫測試和文檔

---

**最後更新**: 2024-11-23  
**版本**: 2.0  
**聯繫**: 查看 README.md
