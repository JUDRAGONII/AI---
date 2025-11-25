# 系統部署指南

完整的生產環境部署與維運指南

## 📋 部署前檢查清單

### 環境需求
- [x] Docker Desktop 已安裝
- [x] Python 3.11+ 已安裝
- [x] Node.js 18+ 已安裝
- [x] 至少 8GB RAM
- [x] 50GB 可用硬碟空間

### 配置檢查
- [ ] 所有 API Keys 已填入 `.env`
- [ ] 資料庫密碼已設定
- [ ] N8N 認證已配置
- [ ] 備份目錄已建立

## 🚀 完整部署步驟

### 步驟 1: 環境準備

```bash
# 1. 克隆或進入專案目錄
cd c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫

# 2. 複製環境變數範例
cp config/.env.example config/.env
cp frontend/.env.example frontend/.env

# 3. 編輯 config/.env 填入所有必要的 API Keys
notepad config/.env

# 4. 編輯 frontend/.env 設定 Supabase 連線
notepad frontend/.env
```

### 步驟 2: 啟動資料庫

```bash
# 啟動 PostgreSQL 和 pgAdmin
docker-compose up -d postgres pgadmin

# 等待資料庫就緒
docker-compose logs -f postgres | grep "database system is ready"

# 檢查資料庫連線
# 訪問 http://localhost:15050 (pgAdmin)
```

### 步驟 3: 初始化資料

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 執行資料回溯（背景執行）
# Phase 1: 黃金與匯率
python scripts/run_backfill.py --phase 1

# Phase 2: 宏觀經濟
python scripts/run_backfill.py --phase 2 &

# Phase 3: 台股價格
python scripts/run_backfill.py --phase 3 &

# Phase 4: 美股價格
python scripts/run_backfill.py --phase 4 &

# 監控進度
python scripts/monitor_backfill.py
```

### 步驟 4: 啟動後端 API

```bash
# 開新終端機視窗
python api_server.py

# API 將運行於 http://localhost:5000
# 測試健康檢查: curl http://localhost:5000/health
```

### 步驟 5: 啟動前端

```bash
# 開新終端機視窗
cd frontend
npm install
npm run dev

# 前端將運行於 http://localhost:5173
```

### 步驟 6: 啟動 N8N 自動化（選用）

```bash
# 啟動包含 N8N 的完整服務
docker-compose --profile full up -d

# N8N 將運行於 http://localhost:5678
```

## 🔧 生產環境配置

### Nginx 反向代理

建立 `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # N8N
    location /n8n {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
    }
}
```

### SSL 憑證（Let's Encrypt）

```bash
# 安裝 certbot
sudo apt-get install certbot python3-certbot-nginx

# 獲取憑證
sudo certbot --nginx -d your-domain.com
```

### 環境變數生產配置

`config/.env`:
```env
# 生產環境設定
FLASK_DEBUG=False
API_PORT=5000

# 資料庫（使用強密碼）
DB_PASSWORD=your_strong_password_here

# 限流設定
RATE_LIMIT_PER_MINUTE=60
```

## 📊 監控與日誌

### 系統監控

```bash
# 監控 Docker 容器
docker stats

# 檢查日誌
docker-compose logs -f postgres
docker-compose logs -f n8n
```

### 資料庫監控

使用 pgAdmin 或執行查詢：

```sql
-- 檢查資料量
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 檢查連線數
SELECT count(*) FROM pg_stat_activity;
```

### 應用日誌

```bash
# API 日誌
tail -f logs/api.log

# N8N 執行日誌
docker-compose logs -f n8n
```

## 💾 備份策略

### 資料庫備份

```bash
# 手動備份
docker exec quant_postgres pg_dump -U postgres quant_db > backup_$(date +%Y%m%d).sql

# 自動備份（使用 N8N 或 cron）
0 4 * * * docker exec quant_postgres pg_dump -U postgres quant_db | gzip > /backups/quant_db_$(date +\%Y\%m\%d).sql.gz
```

### 備份還原

```bash
# 還原資料庫
cat backup_20241123.sql | docker exec -i quant_postgres psql -U postgres quant_db
```

### 程式碼備份

```bash
# 定期推送到 Git
git add .
git commit -m "Backup $(date +%Y%m%d)"
git push
```

## 🔒 安全性加固

### 1. 防火牆設定

```bash
# 僅開放必要端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 2. API 認證

在 `api_server.py` 添加：

```python
from flask import request
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == os.getenv('API_KEY'):
            return f(*args, **kwargs)
        return jsonify({'error': 'Unauthorized'}), 401
    return decorated

@app.route('/api/protected')
@require_api_key
def protected():
    return jsonify({'data': 'sensitive data'})
```

### 3. 速率限制

```bash
pip install flask-limiter

# 在 api_server.py 中
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/endpoint')
@limiter.limit("60 per minute")
def endpoint():
    return jsonify({'data': 'data'})
```

## 📈 效能優化

### 資料庫優化

```sql
-- 建立索引
CREATE INDEX idx_stock_code_date ON tw_stock_prices(stock_code, trade_date);
CREATE INDEX idx_factor_scores ON quant_scores(stock_code, calculation_date);

-- 定期清理
VACUUM ANALYZE;
```

### 快取策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stock_info(stock_code):
    # 快取股票基本資料
    pass
```

## 🚨 故障排除

### 常見問題

**資料庫連線失敗**
```bash
# 檢查容器狀態
docker ps
docker logs quant_postgres

# 重啟資料庫
docker-compose restart postgres
```

**API 無回應**
```bash
# 檢查進程
ps aux | grep python
kill -9 <pid>
python api_server.py
```

**前端無法載入**
```bash
# 清除快取重建
cd frontend
rm -rf node_modules
npm install
npm run dev
```

## 📞 支援資源

- 系統文檔：參閱 `README.md`
- API 文檔：參閱 `API_SERVER_GUIDE.md`
- N8N 配置：參閱 `N8N_WORKFLOW_GUIDE.md`

---

**版本**: 1.0.0  
**最後更新**: 2024-11-23
