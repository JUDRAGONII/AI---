@echo off
chcp 65001
echo ==========================================
echo       AI 投資分析儀 - GitHub 自動上傳
echo ==========================================
echo.

cd /d "c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫"

echo [1/5] 初始化 Git (如果尚未初始化)...
if not exist .git (
    git init
    echo Git 初始化完成
) else (
    echo Git 已初始化
)

echo [2/5] 設定遠端倉庫 (如果需要)...
echo 請確認您已設定 git remote add origin [URL]
echo 如果尚未設定，請手動執行: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

echo [3/5] 添加所有變更...
git add .

echo [4/5] 提交變更...
set "DATE=%date:~0,4%%date:~5,2%%date:~8,2%"
set "TIME=%time:~0,2%%time:~3,2%"
set "TIME=%TIME: =0%"
git commit -m "Auto Update: %DATE%_%TIME% - System Optimization & N8N Integration"

echo [5/5] 推送到 GitHub...
echo 注意：這一步需要您的 GitHub 權限。如果已設定 SSH Key 或 Credential Manager，將自動完成。
git push -u origin main

echo.
echo ==========================================
echo                上傳完成
echo ==========================================
pause
