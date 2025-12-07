@echo off
chcp 65001
cls
echo ==========================================
echo       AI 投資分析儀 - N8N 自動化啟動系統
echo ==========================================
echo.

echo [1/4] 檢查 Node.js 環境...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤：未偵測到 Node.js！
    echo 請前往 https://nodejs.org/ 下載並安裝。
    pause
    exit /b
)
echo ✅ Node.js 已就緒

echo [2/4] 檢查 N8N 安裝狀態...
call n8n --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ N8N 已安裝
    goto START_N8N
)

echo [2/4] N8N 未安裝，正在執行首次安裝...
echo ⚠️ 這可能需要 3-5 分鐘，請耐心等待...
echo 正在執行: npm install -g n8n
call npm install -g n8n --no-fund --no-audit

if %errorlevel% neq 0 (
    echo.
    echo ❌ 安裝失敗！嘗試使用忽略依賴衝突模式...
    call npm install -g n8n --legacy-peer-deps --no-fund --no-audit
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ N8N 安裝遭遇嚴重錯誤，無法繼續。
    echo 請嘗試手動執行: npm install -g n8n
    pause
    exit /b
)

:START_N8N
echo.
echo [3/4] 正在啟動 N8N 伺服器...
echo.
echo 📢 注意：
echo 1. 啟動成功後，瀏覽器將自動打開 http://localhost:5678
echo 2. 請勿關閉此黑色視窗，否則服務將停止
echo 3. 若看到 "Editor is now accessible"，代表已啟動成功
echo.
echo ---------------------------------------------------
echo 正在啟動... (若長時間無反應請按 Ctrl+C 重試)
echo ---------------------------------------------------

call n8n start

if %errorlevel% neq 0 (
    echo.
    echo ❌ N8N 異常終止 (Error Code: %errorlevel%)
    echo 常見原因：
    echo 1. 端口 5678 被佔用 -> 請關閉其他 N8N 實例
    echo 2. 權限不足 -> 請以管理員身分執行
)

echo.
echo ==========================================
echo       服務已結束
echo ==========================================
pause
