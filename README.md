# AI 投資分析儀 (Gemini Quant)

**本地數據霸權，雲端 AI 賦能**

完整的量化投資分析平台，整合宏觀經濟、市場情緒、個股基本面與技術面資訊，透過量化模型與 LLM 生成投資分析報告。

---

## ✨ 系統特色

- 🎯 **六大因子量化分析** - 價值、品質、動能、規模、波動、成長
- 📊 **20+ 技術指標** - MA, EMA, MACD, RSI, KD, 布林通道, ATR 等
- 🤖 **Gemini AI 整合** - 每日戰略報告、決策模板自動生成
- 📈 **TDCC 大戶同步率** - 集保中心權威籌碼資料
- 💼 **投資組合優化** - 效率前緣、蒙地卡羅模擬
- 🔬 **策略回測實驗室** - No-Code 策略建構、完整績效分析
- 🎨 **現代化介面** - React + Tailwind CSS + Dark Mode

---

## 🚀 快速啟動

### 方法一：一鍵啟動腳本（推薦）

**Windows**:
```bash
# 啟動所有服務
start_all.bat

# 停止所有服務
stop_all.bat
```

**跨平台（Python）**:
```bash
# 啟動所有服務
python startup_manager.py start

# 啟動包含 N8N
python startup_manager.py start --n8n

# 停止所有服務
python startup_manager.py stop

# 查看狀態
python startup_manager.py status
```

### 方法二：手動啟動

**前端應用**
```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

**後端API**
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python api_server.py
# http://localhost:5000
```

### 方法三：Docker 完整服務
- ✅ 7 個 API 整合（TWSE, TPEX, TDCC, yfinance, FRED 等）
- ✅ 自動化資料回溯（250K+ 筆）

### 前端應用（React）

**基礎頁面（8/8）** ✅
1. ✅ Dashboard - 市場總覽 + AI 觀點
2. ✅ ShareholderAnalysis - TDCC 大戶同步率分析
3. ✅ FactorDashboard - 六大因子雷達圖
4. ✅ AIInsights - 每日報告展示
5. ✅ TechnicalAnalysis - 價格圖表 + 技術指標
6. ✅ PortfolioManagement - 持股明細 + 風險指標
7. ✅ NewsManagement - RSS 訂閱 + AI 摘要
8. ✅ Settings - 系統設定 + 參數調整

**進階決策頁面（11/11）** 🔥
9. ✅ PortfolioOptimization - 投資組合優化 + 效率前緣
10. ✅ StrategyBacktesting - 策略回測 + 績效分析
11. ✅ PortfolioStressTesting - 壓力測試 + VaR/CVaR
12. ✅ InvestmentGoals - 投資目標追蹤 + 進度分析
13. ✅ AIChatAnalyst - 對話式 AI 分析師
14. ✅ SimilarAssetsFinder - 相似資產發現器
15. ✅ SmartAlertSystem - 智慧事件警報系統
16. ✅ DynamicIntelligence - 動態情報儀表板
17. ✅ AIPortfolioStrategy - AI 投資組合策略
18. ✅ WhatIfSimulator - 假設情境模擬器
19. ✅ BehavioralCoach - 行為金融教練

**管理工具頁面（5/5）** ⚙️
20. ✅ PortfolioDetails - 投資組合明細 + 績效歸因
21. ✅ TransactionLog - 交易日誌 + 理由記錄
22. ✅ AccountManagement - 帳戶管理 + 2FA
23. ✅ APIManagement - API 監控 + 狀態管理
24. ✅ ReportCenter - 報告中心 + 匯出功能

**後端 API（1/1）** ✅
25. ✅ Flask RESTful API - 15個端點完整整合

**總計：25個完整功能模組** 🎯

---

## 🎯 核心功能演示

### 1. 六大因子分析
```python
from calculators import FactorEngine

engine = FactorEngine()
scores = engine.calculate_all_factors('2330', 580.0, 'tw', save_to_db=True)
# 返回：價值、品質、動能、規模、波動、成長、總分
```

### 2. AI 報告生成
```python
from ai.report_generator import DailyReportGenerator

gen = DailyReportGenerator()
report = gen.generate_daily_report()
# 自動生成含市場分析、AI 觀點的 Markdown 報告
```

### 3. 大戶同步率追蹤
```python
from api_clients import TWStockClient

client = TWStockClient()
data = client.get_shareholder_dispersion_from_tdcc('2330')
# 返回：15 個持股級距 + 同步率指標 + 資金流向
```

---

## 📈 技術棧

### 後端
- Python 3.11+
- PostgreSQL 15
- Google Gemini 2.0 Flash
- Supabase (Self-Hosted)

### 前端
- React 18
- Vite
- Tailwind CSS
- Recharts
- React Router v6

### 資料來源
- TWSE/TPEX OpenAPI（台股）
- TDCC Open Data（股權分散）
- yfinance（美股）
- FRED API（宏觀經濟）
- Alpha Vantage（新聞）

---

## 🎨 介面預覽

系統包含：
- 📊 15+ Recharts 互動圖表
- 🌓 完整 Dark Mode 支援
- 📱 響應式設計（Desktop/Tablet優先）
- 🎯 直覺導航與快速操作

---

## 📊 開發進度


```bash
# 必要
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=15432
DB_NAME=quant_db
DB_USER=postgres
DB_PASSWORD=your_password

# 選用
TIINGO_API_KEY=your_tiingo_key
FRED_API_KEY=your_fred_key
ALPHA_VANTAGE_API_KEY=your_av_key
```

---

## 📝 授權

本專案為私人開發專案。

---

## 🚀 持續開發中

系統正持續開發更多進階功能，敬請期待！

**最後更新**: 2024-11-23
