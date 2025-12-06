# Supabase Docker 部署指南

## 當前狀態
✅ 技術分析頁面修復完成（日期格式與排序問題已解決）
✅ 環境變數檔案已建立 (`supabase_config/supabase.env`)
✅ Docker Compose 配置已複製
✅ Volumes 配置已複製

## 啟動 Supabase

### 1. 更新環境變數
編輯 `supabase_config/supabase.env`，至少更新以下關鍵值：
- `POSTGRES_PASSWORD`
- `JWT_SECRET`
- `SECRET_KEY_BASE`
- `VAULT_ENC_KEY`
- `DASHBOARD_PASSWORD`

### 2. 啟動服務
```powershell
cd supabase_config
docker compose --env-file supabase.env up -d
```

### 3. 檢查服務狀態
```powershell
docker compose ps
```

### 4. 訪問 Supabase Studio
打開瀏覽器訪問：http://localhost:3001

### 5. 配置前端

在前端專案中安裝 Supabase 客戶端：
```bash
npm install @supabase/supabase-js
```

建立 Supabase 客戶端（`frontend/src/lib/supabase.js`）：
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'http://localhost:8000'
const supabaseAnonKey = 'YOUR_ANON_KEY_FROM_ENV'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

## 端口映射
- Kong API Gateway: http://localhost:8000
- Supabase Studio: http://localhost:3001  
- Realtime: 內部端口 4000（透過 Kong 訪問）
- PostgreSQL: 內部端口 5432（透過 Kong 訪問）

## 停止服務
```powershell
cd supabase_config
docker compose down
```

## 清理所有數據
```powershell
cd supabase_config
docker compose down -v
```

## 常見問題

### 端口被佔用
如果端口 8000 或 3001 被佔用，編輯 `supabase.env`：
```
KONG_HTTP_PORT=8001  # 更改為其他端口
```

### 服務啟動失敗
查看日誌：
```powershell
docker compose logs supabase-kong
docker compose logs supabase-db
```

### 資料庫連接問題
確認 PostgreSQL 容器已啟動並健康：
```powershell
docker compose ps
docker compose exec  db pg_isready
```
