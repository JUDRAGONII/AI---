# pgAdmin 查看資料回溯進度教學

## 📊 如何在 pgAdmin 查看資料庫回溯進度

### 步驟 1：登入 pgAdmin

1. 瀏覽器開啟：**http://localhost:8080**
2. 登入資訊：
   - Email: `admin@example.com`
   - Password: `admin`

### 步驟 2：連接資料庫伺服器

1. 左側選單中，右鍵點擊 **Servers**
2. 選擇 **Register → Server**
3. 填入連線資訊：
   
   **General 標籤**：
   - Name: `Financial Database`
   
   **Connection 標籤**：
   - Host: `postgres`（容器名稱，不是 localhost！）
   - Port: `5432`（容器內部端口）
   - Maintenance database: `financial_data`
   - Username: `postgres`
   - Password: `0824-003-a-8-Po`（與 docker-compose.yml 一致）
   
4. 點擊 **Save**

### 步驟 3：查看資料表

1. 展開左側樹狀結構：
   ```
   Servers
   └─ Financial Database
      └─ Databases
         └─ financial_data
            └─ Schemas
               └─ public
                  └─ Tables
   ```

2. 應該可以看到所有表格（20個）：
   - `tw_stock_prices` - 台股價格
   - `us_stock_prices` - 美股價格
   - `gold_prices` - 黃金價格
   - `exchange_rates` - 匯率
   - `sync_status` - 同步狀態
   - ... 等

### 步驟 4：查看資料（方法一：直接查看）

1. 右鍵點擊 `tw_stock_prices` 表格
2. 選擇 **View/Edit Data → All Rows**
3. 即可看到所有台股價格資料
4. 可以按欄位排序、篩選

### 步驟 5：查看資料（方法二：執行 SQL 查詢）

1. 點擊上方工具列的 **Query Tool** 圖標（或按 Alt+Shift+Q）
2. 在 SQL 編輯器中輸入查詢：

```sql
-- 查看台股資料筆數
SELECT COUNT(*) as total_records 
FROM tw_stock_prices;

-- 查看最新的10筆台股資料
SELECT stock_code, trade_date, close_price, volume
FROM tw_stock_prices
ORDER BY trade_date DESC
LIMIT 10;

-- 查看台積電（2330）的資料
SELECT trade_date, open_price, high_price, low_price, close_price, volume
FROM tw_stock_prices
WHERE stock_code = '2330'
ORDER BY trade_date DESC
LIMIT 20;

-- 查看美股資料筆數
SELECT COUNT(*) as total_records
FROM us_stock_prices;

-- 查看 Apple（AAPL）的資料
SELECT trade_date, open_price, high_price, low_price, close_price, volume
FROM us_stock_prices
WHERE symbol = 'AAPL'
ORDER BY trade_date DESC
LIMIT 20;
```

3. 點擊 **Execute/Refresh** 按鈕（▶️ 圖標）或按 F5 執行
4. 結果會顯示在下方的 **Data Output** 區域

### 步驟 6：監控回溯進度

查看同步狀態表：

```sql
-- 查看所有同步狀態
SELECT 
    data_source,
    source_identifier,
    sync_status,
    total_records,
    earliest_date,
    latest_date,
    updated_at
FROM sync_status
ORDER BY updated_at DESC;

-- 只看成功的
SELECT 
    data_source,
    source_identifier,
    total_records,
    latest_date
FROM sync_status
WHERE sync_status = 'success'
ORDER BY data_source, source_identifier;

-- 看失敗的（如果有）
SELECT *
FROM sync_status
WHERE sync_status = 'failed';
```

### 步驟 7：即時刷新查看新資料

當資料回溯程式正在執行時：

1. 定期執行 COUNT 查詢查看筆數增加：
```sql
SELECT 
    (SELECT COUNT(*) FROM tw_stock_prices) as taiwan_stocks,
    (SELECT COUNT(*) FROM us_stock_prices) as us_stocks,
    (SELECT COUNT(*) FROM gold_prices) as gold_records,
    (SELECT COUNT(*) FROM exchange_rates) as exchange_rates;
```

2. 每隔 10-30 秒點擊 **Execute** 重新執行
3. 觀察數字是否增加

### 步驟 8：視覺化查詢結果

pgAdmin 提供圖表功能：

1. 執行查詢後，點擊結果面板的 **Graph** 標籤
2. 選擇圖表類型（折線圖、長條圖等）
3. 設定 X 軸（如 trade_date）和 Y 軸（如 close_price）
4. 即可看到視覺化圖表

---

## 🔍 常用查詢範例

### 查看每個股票的資料筆數

```sql
SELECT stock_code, COUNT(*) as records
FROM tw_stock_prices
GROUP BY stock_code
ORDER BY records DESC;
```

### 查看日期範圍

```sql
SELECT 
    MIN(trade_date) as earliest_date,
    MAX(trade_date) as latest_date,
    COUNT(DISTINCT trade_date) as trading_days
FROM tw_stock_prices
WHERE stock_code = '2330';
```

### 查看最近回溯的資料

```sql
SELECT *
FROM sync_status
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;
```

---

## 💡 提示

- **重要**：連接時 Host 使用 `postgres`（容器名稱），不是 `localhost`
- pgAdmin 的查詢會話會過期，如果連線中斷請重新連接
- 可以儲存常用查詢：右鍵點擊查詢 → Save
- 可以匯出查詢結果：右鍵點擊結果 → Download as CSV

現在您可以在 pgAdmin 即時監控資料回溯進度了！🎉
