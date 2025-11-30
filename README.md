# AI投資分析儀 (Gemini Quant) v1.0

**台美股量化投資決策平台** | 完成度: 100% 🎉

一個整合AI智能分析、量化因子、技術指標的專業投資工具。基於Google Gemini AI，提供即時市場分析、投資組合管理、策略回測等完整功能。

---

## ✨ 核心特色

- 🤖 **AI智能分析** - Gemini API深度整合，自動生成市場分析與投資建議
- 📊 **量化引擎** - 6大量化因子 + 7種技術指標
- 💼 **投資組合管理** - 多組合管理、績效追蹤、風險分析
- 📈 **即時數據** - WebSocket即時推送、Redis快取加速
- 🎯 **策略回測** - No-Code策略建構、歷史回測驗證
- 🌓 **精美UI** - Dark Mode、響應式設計、現代化介面

---

## 📊 系統狀態

| 項目 | 狀態 | 數量/完成度 |
|------|------|------------|
| 資料庫表格 | ✅ | 24個 |
| API端點 | ✅ | 17個(14基礎+3AI) |
| 前端頁面 | ✅ | 43個 |
| 市場數據 | ✅ | 57,465筆 |
| 台股數據 | ✅ | 138支，30,544筆 |
| 美股數據 | ✅ | 100支，25,001筆 |
| 技術指標 | ✅ | 7種 |
| 量化因子 | ✅ | 6大類 |
| 系統完成度 | ✅ | 100% |

---

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 15

### 1. 克隆專案
```bash
git clone https://github.com/your-repo/gemini-quant.git
cd gemini-quant
```

### 2. 啟動Docker資料庫
```bash
docker-compose up -d
```

### 3. 後端設置
```bash
# 安裝Python依賴
pip install -r requirements.txt

# 設置環境變數（複製.env.example到config/.env並填入API金鑰）
cp config/.env.example config/.env

# 啟動API服務器
python api_server_v3.py
```

### 4. 前端設置
```bash
cd frontend
npm install
npm run dev
```

### 5. 訪問系統
- **前端**: http://localhost:5174
- **API**: http://localhost:5000
- **WebSocket**: http://localhost:5001
- **pgAdmin**: http://localhost:15050

---

## 📂 專案結構

```
├── api_server_v3.py           # API服務器 (Flask)
├── websocket_server.py        # WebSocket即時推送
├── calculators/               # 量化計算引擎
│   ├── indicators.py          # 技術指標 (MA/RSI/MACD/Bollinger/KD/ATR)
│   └── factors.py             # 量化因子 (價值/品質/動能/成長/規模/波動)
├── ai_clients/                # AI整合
│   └── gemini_client.py       # Gemini API客戶端
├── scripts/                   # 數據同步腳本
│   ├── massive_data_sync.py   # 大規模數據同步
│   ├── generate_ai_reports.py # AI報告生成
│   └── sync_tdcc_shareholder.py # TDCC大戶持股同步
├── utils/                     # 工具模組
│   └── cache.py               # Redis快取管理
├── database/                  # 資料庫
│   └── schema.sql             # Schema定義 (24表)
├── frontend/                  # React前端
│   ├── src/
│   │   ├── pages/             # 43個功能頁面
│   │   ├── components/        # React組件
│   │   └── services/          # API服務層
│   └── package.json
├── tests/                     # 測試
│   └── system_test.py         # 系統完整性測試
└── docker-compose.yml         # Docker配置
```

---

## 🔌 API端點

### 基礎端點
- `GET /api/health` - 健康檢查
- `GET /api/stocks/list` - 股票列表 (台股/美股)
- `GET /api/stocks/<code>` - 股票詳情
- `GET /api/prices/<code>` - 價格歷史

### 技術指標
- `GET /api/indicators/<code>/ma` - 移動平均
- `GET /api/indicators/<code>/rsi` - RSI指標
- `GET /api/indicators/<code>/macd` - MACD
- `GET /api/indicators/<code>/bollinger` - 布林通道

### 市場數據
- `GET /api/commodity/<code>` - 商品價格 (黃金/白銀/原油)
- `GET /api/forex/<pair>` - 匯率數據
- `GET /api/market/summary` - 市場總覽

### AI分析
- `GET /api/ai/test-connection` - AI連接測試
- `POST /api/ai/analyze-stock/<code>` - 個股AI分析
- `POST /api/ai/market-report` - 市場分析報告

更多詳情請見 [API 文檔](./README_API_v2.5.md)

---

## 🎨 主要功能頁面

### 第一層：核心基礎
1. **Dashboard** - 投資指揮中心（含黃金與匯率統計）
2. **MarketOverview** - 市場總覽
3. **StockListTW/US** - 台美股列表
4. **PortfolioManagement** - 投資組合管理
5. **TransactionLog** - 交易日誌

### 第二層：洞察分析
6. **AIHouseView** - AI統一觀點（市場分析報告）
7. **TechnicalAnalysis** - 技術分析中心
8. **FactorDashboard** - 因子投資儀表板
9. **DynamicIntelligence** - 動態情報儀表板

### 第三層：決策輔助
10. **AIPortfolioStrategy** - AI投資組合策略
11. **PortfolioOptimization** - 投資組合優化
12. **StrategyBacktesting** - 策略回測實驗室
13. **PortfolioStressTesting** - 壓力測試
14. **SimilarAssetsFinder** - 相似資產發現器

### 第四層：紀律與成長
15. **InvestmentGoals** - 投資目標設定
16. **StrategyTracker** - 策略績效追蹤
17. **BehavioralCoach** - AI行為金融教練

完整清單共43個頁面

---

## 🧪 測試

### 執行系統測試
```bash
python tests/system_test.py
```

測試項目：
- ✅資料庫連接
- ✅ 17個API端點
- ✅ AI功能連接
- ✅ 數據完整性

---

## 📦 數據同步

### 大規模數據同步
```bash
python scripts/massive_data_sync.py
```

### TDCC大戶持股同步
```bash
# 同步所有股票
python scripts/sync_tdcc_shareholder.py sync

# 測試單一股票
python scripts/sync_tdcc_shareholder.py test 2330

# 計算大戶同步率
python scripts/sync_tdcc_shareholder.py ratio 2330
```

### AI報告生成
```bash
# 生成市場分析報告
python scripts/generate_ai_reports.py market

# 生成個股分析報告
python scripts/generate_ai_reports.py stock 2330
```

---

## 🛠️ 技術棧

### 後端
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 15
- **Cache**: Redis 7.0
- **WebSocket**: Flask-SocketIO
- **AI**: Google Gemini API

### 前端
- **Framework**: React 18 + Vite
- **Router**: React Router v6
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React

### 數據源
- **台股**: TWSE OpenAPI
- **美股**: yfinance
- **TDCC**: TDCC OpenAPI
- **商品/匯率**: yfinance

---

## 📈 數據統計

- **資料表**: 24個
- **總數據量**: 57,465筆
- **台股**: 138支股票，30,544筆價格數據
- **美股**: 100支股票，25,001筆價格數據
- **商品**: 5種（黃金/白銀/原油/銅/天然氣），1,255筆
- **匯率**: 5對（USD/TWD/EUR/JPY/GBP/CNY），665筆
- **技術指標**: 7種
- **量化因子**: 6大類

---

## 🔐 環境變數配置

在 `config/.env` 設置以下變數：

```env
# 資料庫
DB_HOST=localhost
DB_PORT=15432
DB_NAME=quant_db
DB_USER=postgres
DB_PASSWORD=postgres

# API Port
API_PORT=5000

# Google AI API Key
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Redis (可選)
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 📝 版本歷史

### v1.0.0 (2025-11-30) 🎉
- ✅ 核心功能100%完成
- ✅ 43個前端頁面
- ✅ 17個API端點
- ✅ AI功能完整整合
- ✅ WebSocket即時推送
- ✅ Redis快取加速
- ✅ TDCC大戶持股同步
- ✅ 系統測試腳本

---

## 🤝 貢獻

歡迎提交Issue或Pull Request！

---

## 📄 授權

MIT License

---

## 👨‍💻 開發者

開發者: AI Agent (Gemini 2.5 Flash Thinking)  
專案: AI投資分析儀 (Gemini Quant)  
完成日期: 2025-11-30

---

## 📞 聯絡方式

如有問題請開Issue或聯絡專案維護者。

---

**⚠️ 免責聲明**: 本系統僅供學習與研究使用，不構成任何投資建議。投資有風險，決策需謹慎。
