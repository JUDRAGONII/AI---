# AI 投資分析儀系統

> 專業級量化投資分析平台，整合AI決策、技術分析、籌碼追蹤、投資組合管理

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 目錄

- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [快速開始](#快速開始)
- [API文檔](#api文檔)
- [開發指南](#開發指南)
- [常見問題](#常見問題)

---

## ✨ 功能特色

### 🤖 AI智能分析
- **六因子評分系統**: 宏觀環境、技術面、籌碼面、基本面、市場情緒、估值水平
- **統合決策報告**: Gemini AI驅動的深度分析報告
- **雷達圖視覺化**: 直觀展示多維度評分

### 📊 股價深度分析
- **位階判斷**: 52週高低點位階分析
- **趨勢分析**: MA排列、趨勢強度、多空判斷
- **量價關係**: 價漲量增/價漲量縮/背離檢測
- **技術指標**: RSI, MACD, KD, Williams, 布林通道
- **綜合評分**: 0-100分多維度評分系統

### 💰 籌碼追蹤
- **三大法人**: 外資/投信/自營商買賣超統計
- **連續天數**: 連續買超/賣超天數追蹤
- **融資融券**: 使用率、資券比、風險警示
- **主導力量**: 自動判斷籌碼主導方

### 📈 投資組合管理
- **持倉管理**: 新增/刪除/查詢持倉
- **績效計算**: 即時損益、報酬率統計
- **交易記錄**: 完整交易歷史追蹤
- **費用計算**: 自動計算手續費與證交稅

### 📰 技術分析中心
- **K線圖表**: TradingView風格圖表
- **訊號標註**: 黃金交叉/死亡交叉/RSI超買超賣
- **指標面板**: MA20, RSI, MACD即時數值
- **歷史回測**: 訊號準確度追蹤

### ⚙️ 自動化系統
- **N8N工作流**: 台股/美股數據自動更新
- **定時報告**: AI報告自動生成
- **智慧警報**: 多條件監控觸發

---

## 🏗️ 系統架構

### 技術棧

**後端**
- Framework: Flask 3.1.2
- Database: PostgreSQL 15
- AI Model: Google Gemini 2.5 Flash
- Data Processing: pandas, numpy
- WebSocket: Flask-SocketIO

**前端**
- Framework: React 18 + Vite
- UI: TailwindCSS + Lucide Icons
- Charts: Recharts
- Routing: React Router v6
- State: React Hooks

**基礎設施**
- Container: Docker Desktop
- Automation: N8N
- Version Control: Git

### 專案結構

```
台股美股金融資料庫/
├── calculators/              # 分析計算器模組
│   ├── position_analyzer.py  # 位階分析
│   ├── technical_indicators.py # 技術指標
│   ├── institutional_analyzer.py # 三大法人
│   └── margin_analyzer.py    # 融資融券
├── api_server_v5.py          # 主API伺服器
├── chips_api.py              # 籌碼分析API
├── portfolio_api.py          # 投資組合API
├── transaction_api.py        # 交易API
├── signals_api.py            # 訊號API
├── frontend/                 # 前端應用
│   ├── src/
│   │   ├── pages/           # 頁面組件
│   │   └── components/      # 共用組件
│   └── package.json
├── database/                 # 資料庫schema
├── config/                   # 環境配置
└── n8n_config/              # N8N配置
```

---

## 🚀 快速開始

### 環境需求

- **Python**: 3.11+
- **Node.js**: 20+
- **Docker Desktop**: 最新版
- **PostgreSQL**: 15 (透過Docker)

### 安裝步驟

#### 1. 資料庫啟動

```bash
# 啟動PostgreSQL容器
docker start quant_postgres

# 如果容器不存在，建立新容器
docker run --name quant_postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=quant_db \
  -p 15432:5432 \
  -d postgres:15
```

#### 2. 後端設定

```bash
# 安裝Python依賴
pip install -r requirements.txt

# 設定環境變數
cp config/.env.example config/.env
# 編輯 config/.env 填入 GEMINI_API_KEY

# 啟動API Server
python api_server_v5.py
```

#### 3. 前端設定

```bash
# 進入前端目錄
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

#### 4. 訪問系統

- **前端**: http://localhost:5173
- **API**: http://localhost:5000
- **API文檔**: http://localhost:5000/api/health

---

## 📡 API文檔

### 系統管理

#### 健康檢查
```http
GET /api/health
```

**回應範例**:
```json
{
  "status": "healthy",
  "version": "v5.0-深度分析版",
  "database": "connected",
  "features": ["depth_analysis", "chips_analysis", "ai_reports"]
}
```

### 股價深度分析

#### 完整深度分析
```http
GET /api/analysis/depth/{stock_code}?market=tw
```

**參數**:
- `stock_code`: 股票代碼 (例: 2330)
- `market`: tw (台股) 或 us (美股)

**回應範例**:
```json
{
  "stock_code": "2330",
  "position_analysis": {
    "current_price": 589.0,
    "level": "中檔區",
    "percentile_52w": 49.8
  },
  "trend_analysis": {
    "trend": "上升趨勢",
    "ma_alignment": "偏多",
    "strength": 68.5
  },
  "comprehensive_judgment": {
    "recommendation": "偏多持有",
    "score": 62.5,
    "confidence": "中"
  }
}
```

### 籌碼分析

#### 三大法人分析
```http
GET /api/chips/{stock_code}/institutional?days=20
```

#### 融資融券分析
```http
GET /api/chips/{stock_code}/margin
```

#### 完整籌碼分析
```http
GET /api/chips/{stock_code}/all
```

### AI報告

#### 獲取報告列表
```http
GET /api/ai-reports?type=unified_decision&limit=30
```

---

## 🛠️ 開發指南

### 添加新計算器

1. 在 `calculators/` 目錄建立新檔案
2. 實作計算邏輯
3. 更新 `calculators/__init__.py`
4. 撰寫單元測試

範例:
```python
# calculators/my_analyzer.py
class MyAnalyzer:
    @staticmethod
    def analyze(data):
        # 分析邏輯
        return result
```

### 添加新API端點

1. 建立Blueprint檔案 (例: `my_api.py`)
2. 定義路由與處理函數
3. 在 `api_server_v5.py` 註冊Blueprint

範例:
```python
# my_api.py
from flask import Blueprint
my_api = Blueprint('my_api', __name__)

@my_api.route('/api/my-endpoint')
def my_endpoint():
    return jsonify({'data': 'value'})

# api_server_v5.py
from my_api import my_api
app.register_blueprint(my_api)
```

### 添加新前端頁面

1. 在 `frontend/src/pages/` 建立組件
2. 在 `App.jsx` 添加路由
3. 在 `Sidebar.jsx` 添加菜單項

---

## ❓ 常見問題

### Q: API返回404錯誤？
A: 確認API Server已啟動，並檢查端點路徑是否正確。使用 `/api/health` 測試連接。

### Q: 前端無法連接後端？
A: 檢查 `frontend/src/services/api.js` 的API_BASE_URL設定。

### Q: 資料庫連接失敗？
A: 確認PostgreSQL容器運行中 (`docker ps`)，並檢查 `config/.env` 的資料庫配置。

### Q: AI報告生成失敗？
A: 檢查 `GEMINI_API_KEY` 是否正確設定，並確認API額度未超限。

---

## 📊 系統狀態

### 功能完成度

| 模組 | 完成度 | 狀態 |
|------|--------|------|
| Dashboard | 100% | ✅ |
| 投資組合管理 | 100% | ✅ |
| 交易日誌 | 100% | ✅ |
| 技術分析 | 100% | ✅ |
| AI統一觀點 | 100% | ✅ |
| 深度分析 | 100% | ✅ |
| 籌碼分析 | 50% | 🟡 |
| 對話式AI | 0% | ⏳ |

**總體完成度**: 49%

### API端點統計
- **運行中**: 18個
- **開發中**: 5個
- **計畫中**: 12個

---

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

### 開發流程
1. Fork專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟Pull Request

---

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 檔案

---

## 🙏 致謝

- **AI Model**: Google Gemini 2.5 Flash
- **數據來源**: Yahoo Finance, 台灣證券交易所
- **UI靈感**: TradingView, Bloomberg Terminal

---

## 📞 聯絡方式

- **專案Repository**: [GitHub連結]
- **問題回報**: [Issues](../../issues)
- **功能建議**: [Discussions](../../discussions)

---

**最後更新**: 2025-12-05  
**版本**: v1.0.0 (Beta)
