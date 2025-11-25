@echo off
echo ====================================
echo AI 投資分析儀 - 停止所有服務
echo ====================================
echo.

echo [1/3] 停止前端和 API 服務...
taskkill /FI "WINDOWTITLE eq Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq API Server*" /F >nul 2>&1
echo ✅ 前端和 API 服務已停止

echo.
echo [2/3] 停止 Docker 容器...
docker-compose down
echo ✅ Docker 容器已停止

echo.
echo [3/3] 清理完成
echo ====================================
echo 🛑 所有服務已停止
echo ====================================
echo.
pause
