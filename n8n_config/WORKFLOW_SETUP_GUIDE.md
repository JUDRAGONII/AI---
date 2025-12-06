# N8N 自動化工作流配置指南

## 📋 前置條件
- ✅ N8N 容器已部署並運行 (http://localhost:5678)
- ✅ PostgreSQL 資料庫 quant_postgres 運行中 (localhost:15432)
- ✅ tw_stock_prices 與 us_stock_prices 表格已存在

## 🚀 訪問 N8N Web UI

1. 瀏覽器開啟 http://localhost:5678
2. 首次訪問會要求設置帳戶（email + 密碼）
3. 登入後進入主界面

## 📊 工作流一：台股盤後數據更新

### 步驟 1：建立新工作流
1. 點擊左上角「+ Workflow」
2. 工作流命名：`TW_Stock_Daily_Update`

### 步驟 2：添加 Cron 觸發器
1. 點擊「+」按鈕 → 選擇「Schedule Trigger」
2. 配置參數：
   - Trigger Times: Trigger at specific tim (cid:57277)e
   - Hour: 14
   - Minute: 30
   - Timezone: Asia/Taipei
   - Trigger Days: Monday to Friday

### 步驟 3：添加 PostgreSQL 節點（獲取股票清單）
1. 添加節點 → 選擇「Postgres」
2. 配置連線：
   - Host: host.docker.internal (或 quant_postgres 容器名稱)
   - Database: quant_db
   - User: postgres
   - Password: (資料庫密碼)
   - Port: 15432
3. 操作類型：Execute Query
4. Query:
   ```sql
   SELECT DISTINCT stock_code 
   FROM tw_stock_prices 
   WHERE market = 'tw' 
   LIMIT 10
   ```

### 步驟 4：添加 Code 節點（獲取 Yahoo Finance 數據）
1. 添加節點 → 選擇「Code」
2. 模式：Run Once for Each Item
3. JavaScript 代碼：
   ```javascript
   const axios = require('axios');
   
   // 從上一個節點獲取股票代碼
   const stockCode = $input.item.json.stock_code;
   const today = new Date().toISOString().split('T')[0];
   
   try {
     // 使用 Yahoo Finance API (透過 yfinance 或直接 HTTP)
     const response = await axios.get(`https://query1.finance.yahoo.com/v8/finance/chart/${stockCode}.TW`);
     const data = response.data.chart.result[0];
     const quotes = data.indicators.quote[0];
     const timestamps = data.timestamp;
     
     const latestIndex = timestamps.length - 1;
     
     return {
       stock_code: stockCode,
       trade_date: today,
       open_price: quotes.open[latestIndex],
       high_price: quotes.high[latestIndex],
       low_price: quotes.low[latestIndex],
       close_price: quotes.close[latestIndex],
       volume: quotes.volume[latestIndex]
     };
   } catch (error) {
     console.error(`獲取 ${stockCode} 數據失敗:`, error);
     return null;
   }
   ```

### 步驟 5：添加 PostgreSQL 節點（插入數據）
1. 添加節點 → 選擇「Postgres」
2. 操作類型：Insert
3. Table: tw_stock_prices
4. Columns: stock_code, trade_date, open_price, high_price, low_price, close_price, volume
5. **開啟選項**：Replace On Conflict (設定衝突欄位：stock_code + trade_date)

### 步驟 6：啟動工作流
1. 點擊右上角「Save」
2. 點擊「Active」開關啟用定時任務
3. 點擊「Execute Workflow」測試手動執行

## 📊 工作流二：美股收盤數據更新

### 快速複製台股工作流
1. 複製「TW_Stock_Daily_Update」工作流
2. 重新命名為「US_Stock_Daily_Update」

### 調整參數
1. **Cron 觸發器**：
   - Hour: 5
   - Minute: 30
   - 說明：美股收盤為台灣時間 05:00-06:00

2. **PostgreSQL 查詢節點**：
   ```sql
   SELECT DISTINCT stock_code 
   FROM us_stock_prices 
   WHERE market = 'us' 
   LIMIT 10
   ```

3. **Code 節點**：
   - 將 `${stockCode}.TW` 改為 `${stockCode}` (美股無需後綴)

4. **PostgreSQL 插入節點**：
   - Table: us_stock_prices

5. 啟用工作流

## 🔍 驗證數據更新

### 檢查 N8N 執行記錄
1. 左側邊欄點擊「Executions」
2. 查看最近執行狀態
3. 點擊任一執行記錄查看詳細 Log

### 檢查資料庫
執行 SQL 查詢確認數據：
```sql
-- 台股
SELECT stock_code, trade_date, close_price 
FROM tw_stock_prices 
WHERE trade_date = CURRENT_DATE;

-- 美股
SELECT stock_code, trade_date, close_price 
FROM us_stock_prices 
WHERE trade_date = CURRENT_DATE;
```

## ⚠️ 注意事項

1. **Docker 容器內存取主機資料庫**：
   - 使用 `host.docker.internal` 而非 `localhost`
   - 或設定 Docker network 讓 n8n 與 quant_postgres 在同一網絡

2. **Yahoo Finance API 限制**：
   - 免費版有請求頻率限制
   - 若大量股票更新，建議分批處理或加入延遲

3. **錯誤處理**：
   - N8N 自動重試機制：Settings → Error Workflow
   - 可設定通知 Webhook

4. **測試建議**：
   - 先從少量股票（5-10支）開始測試
   - 確認正常後再擴展至完整清單

## 📈 下一步擴展

- 大戶籌碼數據更新 (TDCC Open Data, 每週六)
- 宏觀指標更新 (FRED API, 每日)
- 盤中即時數據 (Fugle API WebSocket)
- AI 報告觸發器 (每日 15:00 自動生成)

## 🔗 相關資源
- [N8N 官方文檔](https://docs.n8n.io/)
- [Yahoo Finance API](https://github.com/ranaroussi/yfinance)
- [N8N Community](https://community.n8n.io/)
