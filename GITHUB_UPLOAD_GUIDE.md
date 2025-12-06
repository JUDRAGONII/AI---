# GitHub 上傳指令與說明

## 📦 GitHub 上傳步驟

### 1. 初始化 Git Repository

```bash
cd "c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫"

# 初始化Git
git init

# 添加所有檔案（排除node_modules等）
git add .

# 首次提交
git commit -m "🎉 初始提交: AI投資分析儀系統 v1.0

✨ 功能特色:
- AI統一觀點（六因子評分系統）
- 股價深度分析（位階/趨勢/量價/技術指標）
- 籌碼分析（三大法人/融資融券）
- 投資組合管理
- 交易日誌系統
- 技術分析中心

📊 系統狀態:
- 功能完成度: 49%
- API端點: 18個
- 前端頁面: 10個
- 資料庫表格: 15個

🛠️ 技術棧:
- Backend: Flask 3.1.2 + PostgreSQL 15
- Frontend: React 18 + Vite + TailwindCSS
- AI: Google Gemini 2.5 Flash
- Automation: N8N

🎯 下一步:
- 籌碼分析前端
- 對話式AI分析師
- N8N工作流配置
"
```

### 2. 創建 .gitignore

已包含在專案中，內容：
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Node
node_modules/
dist/
.parcel-cache/
.next/

# 環境變數
.env
*.env
config/.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# 資料庫
*.db
*.sqlite

# 日誌
*.log
logs/

# 其他
.DS_Store
Thumbs.db
```

### 3. 創建 GitHub Repository

1. 登入 GitHub
2. 點擊右上角 "+" → "New repository"
3. 設定:
   - Repository name: `ai-quant-analysis-system`
   - Description: `AI驅動的量化投資分析系統 - 整合深度分析、籌碼追蹤、投資組合管理`
   - Visibility: Public 或 Private
   - **不要勾選** "Initialize this repository with a README"

### 4. 連接遠端Repository

```bash
# 添加遠端repository（替換成你的GitHub用戶名）
git remote add origin https://github.com/YOUR_USERNAME/ai-quant-analysis-system.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 5. 後續更新

```bash
# 添加變更
git add .

# 提交變更
git commit -m "📝 更新說明"

# 推送到GitHub
git push
```

---

## 📋 提交訊息範本

使用Emoji讓提交訊息更清晰：

- `🎉` - 初始提交
- `✨` - 新功能
- `🐛` - Bug修復
- `📝` - 文檔更新
- `♻️` - 代碼重構
- `⚡` - 性能優化
- `🎨` - UI/樣式更新
- `🔧` - 配置變更
- `🚀` - 部署相關
- `🗃️` - 資料庫變更

範例:
```bash
git commit -m "✨ 新增籌碼分析前端頁面"
git commit -m "🐛 修復API路由404錯誤"
git commit -m "📝 更新README安裝說明"
```

---

## 🔒 安全注意事項

### 確保不上傳敏感資訊

1. ✅ `.env` 檔案已在 `.gitignore`
2. ✅ API Keys 不會上傳
3. ✅ 資料庫密碼不會洩露

### 檢查方式

```bash
# 查看即將提交的檔案
git status

# 查看變更內容
git diff

# 如果不小心添加了敏感檔案
git reset HEAD 檔案名稱
```

---

## 📦 專案大小優化

如果專案過大，考慮：

1. **移除大型檔案**
   ```bash
   # 移除已追蹤的大檔案
   git rm --cached 大檔案路徑
   ```

2. **使用 Git LFS** (Large File Storage)
   ```bash
   # 安裝 Git LFS
   git lfs install
   
   # 追蹤大型檔案
   git lfs track "*.psd"
   git lfs track "*.zip"
   ```

---

## 🎯 Repository 設定建議

### README Badges

在 README.md 頂部添加徽章：

```markdown
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
```

### Topics (標籤)

建議添加以下Topics:
- `ai`
- `machine-learning`
- `stock-analysis`
- `trading`
- `quantitative-finance`
- `react`
- `flask`
- `postgresql`
- `gemini-ai`
- `taiwan-stock`

---

## 📞 疑難排解

### 推送失敗

```bash
# 如果遠端有更新
git pull origin main --rebase
git push
```

### 忘記 .gitignore

```bash
# 清除快取重新添加
git rm -r --cached .
git add .
git commit -m "🔧 修正 .gitignore"
```

---

**準備完成！執行上述指令即可將專案上傳到GitHub。**
