@echo off
echo ====================================
echo AI 投資分析儀 - 一鍵啟動腳本
echo ====================================
echo.

echo [1/5] 檢查 Docker 服務...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安裝或未啟動，請先安裝 Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker 服務正常

echo.
echo [2/5] 啟動資料庫服務...
docker-compose up -d postgres pgadmin
if errorlevel 1 (
    echo ❌ 資料庫啟動失敗
    pause
    exit /b 1
)
echo ✅ 資料庫服務已啟動

echo.
echo [3/5] 等待資料庫就緒（10秒）...
timeout /t 10 /nobreak >nul
echo ✅ 資料庫就緒

echo.
echo [4/5] 啟動後端 API 服務（新視窗）...
start "API Server" cmd /k "python api_server.py"
timeout /t 3 /nobreak >nul
echo ✅ API 服務已啟動於 http://localhost:5000

echo.
echo [5/5] 啟動前端應用（新視窗）...
start "Frontend" cmd /k "cd frontend && npm run dev"
echo ✅ 前端應用已啟動於 http://localhost:5173

echo.
echo ====================================
echo 🎉 系統啟動完成！
echo ====================================
echo.
echo 📊 服務端口：
echo   - 前端應用: http://localhost:5173
echo   - API 服務: http://localhost:5000
echo   - pgAdmin:  http://localhost:15050
echo   - PostgreSQL: localhost:15432
echo.
echo 💡 提示：
echo   - 關閉此視窗不會停止服務
echo   - 要停止所有服務，請執行 stop_all.bat
echo.
pause
