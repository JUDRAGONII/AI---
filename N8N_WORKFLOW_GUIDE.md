# N8N 自動化工作流配置指南

本指南說明如何設定 N8N 自動化工作流程，實現系統的無人值守運行。

## 🚀 N8N 安裝與啟動

### 使用 Docker Compose

```bash
# 啟動 N8N（包含在 docker-compose.yml 中）
docker-compose --profile full up -d

# N8N 將運行於 http://localhost:5678
```

### 首次登入

1. 訪問 http://localhost:5678
2. 使用帳密登入：
   - 使用者名稱：admin（或環境變數設定的值）
   - 密碼：admin（或環境變數設定的值）

## 📊 工作流程設定

### 1. 每日數據更新工作流

**觸發時間**：每日凌晨 2:00

**執行步驟**：
1. **Cron 觸發器** - `0 2 * * *`
2. **HTTP Request** - 呼叫資料回溯腳本
   - URL: `http://host.docker.internal:5000/api/update/daily`
   - Method: POST
3. **條件判斷** - 檢查執行結果
4. **發送通知** - Email/LINE 通知執行狀態

**JSON 配置範例**：
```json
{
  "name": "Daily Data Update",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 2 * * *"
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://host.docker.internal:5000/api/update/daily",
        "method": "POST",
        "options": {}
      },
      "name": "Update Data",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ]
}
```

### 2. AI 報告生成工作流

**觸發時間**：每日上午 6:00

**執行步驟**：
1. **Cron 觸發器** - `0 6 * * *`
2. **HTTP Request** - 生成每日戰略報告
   - URL: `http://host.docker.internal:5000/api/ai/daily-report`
   - Method: POST
3. **等待完成** - 等待報告生成（約2-3分鐘）
4. **發送報告** - Email 發送報告摘要

### 3. 價格警報監控工作流

**觸發頻率**：每5分鐘（交易時段）

**執行步驟**：
1. **Cron 觸發器** - `*/5 9-13 * * 1-5`（週一至週五，9:00-13:30）
2. **資料庫查詢** - 查詢所有活躍警報
3. **迴圈處理** - 逐一檢查警報條件
4. **HTTP Request** - 獲取最新價格
5. **條件判斷** - 比對觸發條件
6. **觸發警報** - LINE/Email 推播通知

### 4. 因子分數更新工作流

**觸發時間**：每週六凌晨 3:00

**執行步驟**：
1. **Cron 觸發器** - `0 3 * * 6`
2. **資料庫查詢** - 獲取所有股票清單
3. **迴圈處理** - 批次計算因子分數
4. **HTTP Request** - 呼叫因子計算 API
5. **資料庫寫入** - 儲存計算結果
6. **生成報告** - 因子變化摘要

### 5. 資料庫備份工作流

**觸發時間**：每日凌晨 4:00

**執行步驟**：
1. **Cron 觸發器** - `0 4 * * *`
2. **Execute Command** - 執行 pg_dump
   ```bash
   pg_dump -h postgres -U postgres -d quant_db > /backups/quant_db_$(date +%Y%m%d).sql
   ```
3. **壓縮備份檔** - gzip 壓縮
4. **上傳雲端** - 上傳至 Google Drive / Dropbox
5. **清理舊備份** - 保留最近30天

## 🔧 進階設定

### 環境變數設定

在 `docker-compose.yml` 中設定：

```yaml
n8n:
  environment:
    - DB_TYPE=postgresdb
    - DB_POSTGRESDB_HOST=postgres
    - DB_POSTGRESDB_PORT=5432
    - DB_POSTGRESDB_DATABASE=quant_db
    - DB_POSTGRESDB_USER=postgres
    - DB_POSTGRESDB_PASSWORD=your_password
    - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
    - EXECUTIONS_DATA_SAVE_ON_ERROR=all
```

### 連接本機服務

在 N8N 工作流中連接主機服務時，使用：
- Windows/Mac: `http://host.docker.internal:5000`
- Linux: `http://172.17.0.1:5000`

### 憑證管理

1. **API Keys** - 在 N8N 憑證管理中新增
2. **資料庫連線** - PostgreSQL 憑證
3. **Email SMTP** - Gmail App Password
4. **LINE Notify** - LINE Token

## 📝 工作流範本

### 完整的每日作業流程

```
[Cron 2:00] 
   ↓
[更新台股價格]
   ↓
[更新美股價格]
   ↓
[更新TDCC籌碼]
   ↓
[Cron 6:00]
   ↓
[生成AI報告]
   ↓
[發送Email通知]
   ↓
[備份資料庫]
```

## 🎯 最佳實踐

1. **錯誤處理**
   - 每個節點添加錯誤分支
   - 記錄錯誤日誌到資料庫
   - 發送錯誤通知

2. **效能優化**
   - 批次處理減少API請求
   - 使用快取減少重複查詢
   - 合理設定執行間隔

3. **監控與日誌**
   - 啟用執行歷史記錄
   - 定期檢查失敗任務
   - 建立執行時間監控

## 🔒 安全性

1. **存取控制**
   - 啟用基本認證
   - 設定強密碼
   - 限制 IP 存取

2. **資料保護**
   - 使用環境變數存放敏感資訊
   - 定期更換 API Keys
   - 加密備份檔案

## 📚 資源連結

- [N8N 官方文檔](https://docs.n8n.io/)
- [工作流範本](https://n8n.io/workflows)
- [社群論壇](https://community.n8n.io/)

---

**版本**: 1.0.0  
**最後更新**: 2024-11-23
