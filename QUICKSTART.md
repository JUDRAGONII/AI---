# AI 投資分析儀 (Gemini Quant) - 快速啟動指南

## 🚀 10分鐘快速上手

### 前置需求

- Docker Desktop
- Python 3.11+
- Node.js 18+
- Git

### 步驟 1: 克降專案

```bash
cd c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫
```

### 步驟 2: 環境變數設定

```bash
# 複製環境變數範例
cp config/.env.example config/.env

# 編輯 .env 填入必要的 API Keys
# 最少需要：GEMINI_API_KEY
```

### 步驟 3: 啟動 Docker 服務

```bash
# 啟動 PostgreSQL + pgAdmin
docker-compose up -d postgres pgadmin

# 等待資料庫就緒（約 30 秒）
docker-compose logs -f postgres | grep "database system is ready"

# （選用）啟動完整服務包含 N8N
docker-compose --profile full up -d
```

### 步驟 4: 初始化資料庫

資料庫 schema 會在首次啟動時自動建立。可透過 pgAdmin 確認：

- URL: http://localhost:15050
- Email: admin@quant.local
- Password: admin

### 步驟 5: 執行資料回溯（背景執行）

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# Phase 1: 黃金與匯率（快速，約 5 分鐘）
python scripts/run_backfill.py --phase 1

# Phase 3: 台股價格（較慢，約 2 小時，156K+ 筆）
python scripts/run_backfill.py --phase 3 &

# Phase 4: 美股價格（較慢，約 1.5 小時，91K+ 筆）
python scripts/run_backfill.py --phase 4 &

# 監控回溯進度
python scripts/monitor_backfill.py
```

### 步驟 6: 啟動前端應用

```bash
cd frontend
npm install
npm run dev

# 開啟瀏覽器：http://localhost:5173
```

---

## 📊 系統功能總覽

### 已完成的 10 個頁面

1. **Dashboard** - 市場總覽與 AI 觀點
2. **大戶同步率** - TDCC 籌碼分析（核心功能）
3. **因子投資儀表板** - 六大因子雷達圖
4. **AI 統一觀點** - 每日戰略報告
5. **技術分析** - 價格圖表與技術指標
6. **投資組合管理** - 持股明細與風險分析
7. **新聞管理** - RSS 訂閱與 AI 摘要
8. **系統設定** - 個人化參數調整
9. **投資組合優化** - 效率前緣與蒙地卡羅模擬
10. **策略回測** ​- No-Code 策略建構與回測

---

## 🛠️ 後端功能測試

### 測試六大因子計算

```bash
python
>>> from calculators import FactorEngine
>>> engine = FactorEngine()
>>> scores = engine.calculate_all_factors('2330', 580.0, 'tw')
>>> print(scores)
```

### 測試 AI 報告生成

```bash
python
>>> from ai.report_generator import DailyReportGenerator
>>> gen = DailyReportGenerator()
>>> report = gen.generate_daily_report()
>>> print(report)
```

### 測試 TDCC 大戶籌碼

```bash
python
>>> from api_clients import TWStockClient
>>> client = TWStockClient()
>>> data = client.get_shareholder_dispersion_from_tdcc('2330')
>>> print(data)
```

---

## 📁 專案結構

```
台股美股金融資料庫/
├─ frontend/              # React 前端應用
│  ├─ src/
│  │  ├─ pages/           # 10 個完整頁面
│  │  ├─ components/      # Layout, Sidebar, Header
│  │  └─ App.jsx
│  └─ package.json
│
├─ calculators/           # 量化因子計算模組
│  ├─ factor_engine.py    # 因子整合引擎
│  ├─ value_factor.py     # 價值因子
│  ├─ quality_factor.py   # 品質因子
│  └─ ...
│
├─ ai/                    # AI 模組
│  ├─ gemini_client.py    # Gemini API
│  └─ report_generator.py # 報告生成器
│
├─ api_clients/           # API 客戶端
│  ├─ tw_stock_client.py  # 台股（TWSE/TPEX/TDCC）
│  ├─ us_stock_client.py  # 美股（yfinance）
│  └─ ...
│
├─ database/              # 資料庫
│  └─ schema.sql          # 完整 Schema（30+ 表格）
│
├─ scripts/               # 工具腳本
│  ├─ run_backfill.py     # 資料回溯
│  └─ monitor_backfill.py # 進度監控
│
└─ docker-compose.yml     # Docker 服務配置
```

---

## 🔧 常見問題

### Q: 前端無法連接資料庫？
A: 確認 `frontend/.env` 中的 `VITE_SUPABASE_URL` 設定正確。

### Q: AI 報告生成失敗？
A: 確認 `.env` 中的 `GEMINI_API_KEY` 已填入有效金鑰。

### Q: 資料回溯很慢？
A: 是正常現象。台股156K+筆、美股91K+筆資料需要時間。可放背景執行。

### Q: 如何停止所有服務？
```bash
docker-compose down
```

---

## 📊 服務埠號

| 服務 | 埠號 | 說明 |
|------|------|------|
| PostgreSQL | 15432 | 資料庫 |
| pgAdmin | 15050 | 資料庫管理介面 |
| React 前端 | 5173 | 前端應用 |
| N8N | 5678 | 自動化工作流（選用） |

---

## 🎯 下一步

1. 查看 `README.md` 了解完整功能
2. 查看 `API_EXAMPLES.md` 學習 API 使用
3. 查看 `task.md` 了解開發進度
4. 開始使用前端介面探索系統功能

---

**系統整體進度**: 50% | **前端進度**: 45%

持續開發中，更多功能即將推出！🚀
