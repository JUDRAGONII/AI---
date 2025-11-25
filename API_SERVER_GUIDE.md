# API 服務使用指南

## 🚀 啟動 API 服務

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python api_server.py

# API 服務將運行於 http://localhost:5000
```

## 📡 API 端點

### 健康檢查
```bash
GET /health
```

### 因子分析

**獲取個股因子分數**
```bash
GET /api/factors/2330?market=tw

Response:
{
  "stock_code": "2330",
  "market": "tw",
  "current_price": 580.0,
  "scores": {
    "value_score": 75.2,
    "quality_score": 88.5,
    "momentum_score": 65.8,
    "size_score": 92.1,
    "volatility_score": 68.3,
    "growth_score": 79.6,
    "total_score": 79.7
  }
}
```

**獲取歷史因子分數**
```bash
GET /api/factors/2330/history?days=30&market=tw
```

### AI 報告

**生成每日戰略報告**
```bash
POST /api/ai/daily-report

Response:
{
  "success": true,
  "report": "# 每日戰略投資分析報告..."
}
```

**獲取最新報告**
```bash
GET /api/ai/daily-report
```

**生成個股決策模板**
```bash
POST /api/ai/decision-template/2330
Content-Type: application/json

{
  "market": "tw"
}
```

### TDCC 籌碼資料

**獲取股權分散資料**
```bash
GET /api/tdcc/2330?days=52
```

**獲取最新籌碼**
```bash
GET /api/tdcc/2330/latest
```

### 價格資料

**獲取股價資料**
```bash
GET /api/prices/2330?market=tw&days=252
```

### 技術指標

**計算技術指標**
```bash
GET /api/indicators/2330?market=tw&days=100

Response:
{
  "stock_code": "2330",
  "indicators": {
    "MA5": [...],
    "MA20": [...],
    "RSI": [...],
    "MACD": {...}
  }
}
```

### 股票清單與搜尋

**獲取股票清單**
```bash
GET /api/stocks/list?market=tw
```

**搜尋股票**
```bash
GET /api/stocks/search?q=台積&market=tw
```

## 🔧 環境變數

在 `config/.env` 中設定：

```env
# API 服務
API_PORT=5000
FLASK_DEBUG=False

# 資料庫
DB_HOST=localhost
DB_PORT=15432
DB_NAME=quant_db
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
GEMINI_API_KEY=your_gemini_key
```

## 📊 前端整合範例

```javascript
// 使用 fetch 調用 API
const getFactorScores = async (stockCode) => {
  const response = await fetch(`http://localhost:5000/api/factors/${stockCode}?market=tw`)
  const data = await response.json()
  return data
}

// 使用在 React 元件中
useEffect(() => {
  const loadData = async () => {
    const scores = await getFactorScores('2330')
    console.log(scores)
  }
  loadData()
}, [])
```

## 🎯 Docker 運行

```bash
# 建立 Docker 映像
docker build -t quant-api .

# 運行容器
docker run -p 5000:5000 --env-file config/.env quant-api
```

## 📝 錯誤碼

- `200` - 成功
- `400` - 請求錯誤
- `404` - 找不到資源
- `500` - 伺服器錯誤

## 🔒 安全性

生產環境建議：
1. 啟用 HTTPS
2. 新增 API 認證（JWT）
3.  設定速率限制
4. 啟用 CORS 白名單

---

**版本**: 1.0.0  
**最後更新**: 2024-11-23
