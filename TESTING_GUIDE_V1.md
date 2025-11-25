# AI 投資分析儀 - 系統測試指南

**測試版本**：v1.0 Production Ready  
**測試日期**：2024-11-23  
**功能頁面**：31個

---

## 🚀 快速啟動步驟

### 步驟一：環境檢查

**必要條件**：
- ✅ Docker Desktop 已安裝並運行
- ✅ Node.js 16+ 已安裝
- ✅ Python 3.11+ 已安裝

**檢查命令**：
```bash
# 檢查 Docker
docker --version

# 檢查 Node.js
node --version

# 檢查 Python
python --version
```

### 步驟二：啟動系統

**Windows 一鍵啟動**：
```bash
# 進入專案目錄
cd c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫

# 啟動所有服務
start_all.bat
```

**或分步啟動**：

1. **啟動資料庫**：
```bash
docker-compose up -d
```

2. **啟動前端**：
```bash
cd frontend
npm install
npm run dev
```

3. **啟動後端API**（可選）：
```bash
pip install -r requirements.txt
python api_server.py
```

### 步驟三：訪問系統

**訪問地址**：
- 🎨 **前端界面**：http://localhost:5173
- 🔌 **API服務**：http://localhost:5000
- 📊 **pgAdmin**：http://localhost:15050
- 🤖 **N8N**：http://localhost:5678

---

## 🧪 功能測試清單

### 基礎功能測試（8個頁面）

#### 1. Dashboard（儀表板）
- [ ] 訪問 http://localhost:5173
- [ ] 查看市場總覽數據
- [ ] 檢查 AI 觀點區塊
- [ ] 測試 Dark Mode 切換

#### 2. ShareholderAnalysis（大戶同步率）
- [ ] 輸入股票代碼（如 2330）
- [ ] 查看 15 級距分析
- [ ] 檢查同步率指標

#### 3. FactorDashboard（因子分析）
- [ ] 查看六大因子雷達圖
- [ ] 檢查因子排序功能
- [ ] 測試因子說明

#### 4. TechnicalAnalysis（技術分析）
- [ ] 查看價格圖表
- [ ] 測試技術指標切換
- [ ] 檢查 MACD、RSI 等指標

#### 5. AIInsights（AI 觀點）
- [ ] 查看每日報告
- [ ] 測試 Markdown 渲染
- [ ] 檢查歷史報告

#### 6. PortfolioManagement（投資組合）
- [ ] 查看持股明細
- [ ] 檢查風險指標
- [ ] 測試配置圖表

#### 7. NewsManagement（新聞管理）
- [ ] 測試新聞過濾
- [ ] 查看 AI 摘要
- [ ] 檢查 RSS 訂閱

#### 8. Settings（系統設定）
- [ ] 測試主題切換
- [ ] 調整技術指標參數
- [ ] 修改通知設定

### 進階功能測試（抽樣5個）

#### 9. PortfolioOptimization（組合優化）
- [ ] 查看效率前緣圖
- [ ] 測試蒙地卡羅模擬
- [ ] 檢查優化建議

#### 13. SmartAlertSystem（智慧警報）
- [ ] 設定價格警報
- [ ] 測試警報條件
- [ ] 檢查通知功能

#### 18. WhatIfSimulator（情境模擬）
- [ ] 設定交易情境
- [ ] 查看影響分析
- [ ] 檢查稅務計算

#### 21. CatalystRanker（催化劑排名）
- [ ] 查看 Top 10 資產
- [ ] 檢查觸發條件
- [ ] 測試時間軸切換

#### 31. ScenarioHedging（對沖策略）🆕
- [ ] 選擇情境（經濟衰退）
- [ ] 查看損益模擬
- [ ] 檢查 AI 對沖建議

---

## 🔍 重點測試項目

### 核心功能驗證

**1. 六大因子計算**
```python
# 測試因子計算是否正常
from calculators import FactorEngine

engine = FactorEngine()
scores = engine.calculate_all_factors('2330', 580.0, 'tw')
print(scores)
# 應返回：價值、品質、動能、規模、波動、成長分數
```

**2. API 端點測試**
```bash
# 健康檢查
curl http://localhost:5000/health

# 獲取因子分數
curl http://localhost:5000/api/factors/2330
```

**3. 資料庫連線**
- 訪問 pgAdmin：http://localhost:15050
- 登入帳號：admin@admin.com
- 密碼：admin
- 檢查資料表是否存在

### 性能測試

**1. 頁面載入速度**
- Dashboard 首次載入：< 2秒
- 頁面切換：< 1秒
- 圖表渲染：< 1秒

**2. API 響應時間**
- 健康檢查：< 100ms
- 因子查詢：< 500ms
- 技術指標：< 800ms

### UI/UX 測試

**1. 響應式設計**
- 測試不同螢幕尺寸
- 檢查移動端顯示

**2. Dark Mode**
- 切換主題
- 檢查所有頁面

**3. 導航功能**
- 側邊欄導航
- 麵包屑導航
- 快速搜尋

---

## 🐛 常見問題排查

### 問題1：前端無法啟動

**症狀**：npm run dev 報錯

**解決方案**：
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### 問題2：Docker 容器無法啟動

**症狀**：docker-compose up 失敗

**解決方案**：
```bash
# 停止所有容器
docker-compose down

# 清理並重啟
docker-compose up -d --force-recreate
```

### 問題3：API 無法連接

**症狀**：前端無法獲取 API 數據

**解決方案**：
1. 檢查 API 服務是否運行
2. 檢查端口 5000 是否被占用
3. 檢查 CORS 設定

### 問題4：資料庫連接失敗

**症狀**：無法連接到 PostgreSQL

**解決方案**：
1. 檢查 Docker 容器狀態
2. 確認端口 15432 是否開放
3. 檢查 .env 配置

---

## 📝 測試報告範本

### 測試結果記錄

**測試日期**：____________

**測試人員**：____________

**系統版本**：v1.0

| 功能模組 | 測試狀態 | 備註 |
|---------|---------|------|
| Dashboard | ✅ / ❌ |  |
| 因子分析 | ✅ / ❌ |  |
| 技術分析 | ✅ / ❌ |  |
| AI 觀點 | ✅ / ❌ |  |
| 投資組合 | ✅ / ❌ |  |
| 警報系統 | ✅ / ❌ |  |
| 對沖策略 | ✅ / ❌ |  |

**發現問題**：
1. 
2. 
3. 

**改進建議**：
1. 
2. 
3. 

---

## 🎯 測試建議

### 基礎測試（必做）
1. 啟動系統並訪問 Dashboard
2. 測試 3-5 個核心頁面
3. 檢查基本功能是否正常

### 進階測試（選做）
1. 測試所有 31 個頁面
2. 壓力測試 API 性能
3. 完整的功能流程測試

### 建議測試流程
**第一天**：基礎功能測試（8個頁面）  
**第二天**：進階功能測試（抽樣10個頁面）  
**第三天**：完整測試（全部31個頁面）

---

## 📞 支援資訊

**文檔參考**：
- 快速啟動：`QUICKSTART.md`
- 使用手冊：`USER_MANUAL.md`
- API 文檔：`API_SERVER_GUIDE.md`
- 部署指南：`DEPLOYMENT_GUIDE.md`

**常用命令**：
```bash
# 啟動系統
start_all.bat

# 停止系統
stop_all.bat

# 查看日誌
docker-compose logs -f

# 重啟服務
docker-compose restart
```

---

**祝測試順利！如有問題請參考文檔或提出問題。** 🚀
