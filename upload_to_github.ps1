# GitHub 上傳執行腳本
# 請按照指南依序執行以下命令

# ==========================================
# 步驟 1：設置 Git 用戶資訊（只需執行一次）
# ==========================================
Write-Host "步驟 1：設置 Git 用戶資訊" -ForegroundColor Green
Write-Host "請輸入您的名字（暱稱）：" -ForegroundColor Yellow
$username = Read-Host
git config --global user.name "$username"

Write-Host "請輸入您的 GitHub 郵箱：" -ForegroundColor Yellow
$email = Read-Host
git config --global user.email "$email"

Write-Host "`n✅ Git 用戶資訊設置完成！" -ForegroundColor Green
Write-Host "   名字：$username" -ForegroundColor Cyan
Write-Host "   郵箱：$email" -ForegroundColor Cyan

# ==========================================
# 步驟 2：初始化 Git 倉庫
# ==========================================
Write-Host "`n步驟 2：初始化 Git 倉庫" -ForegroundColor Green
git init
Write-Host "✅ Git 倉庫初始化完成！" -ForegroundColor Green

# ==========================================
# 步驟 3：添加所有文件
# ==========================================
Write-Host "`n步驟 3：添加所有文件到 Git" -ForegroundColor Green
git add .
Write-Host "✅ 文件添加完成！" -ForegroundColor Green

# ==========================================
# 步驟 4：創建提交
# ==========================================
Write-Host "`n步驟 4：創建提交" -ForegroundColor Green
git commit -m "初始提交：AI投資分析儀完整系統"
Write-Host "✅ 提交創建完成！" -ForegroundColor Green

# ==========================================
# 步驟 5：連接 GitHub 倉庫
# ==========================================
Write-Host "`n步驟 5：連接 GitHub 倉庫" -ForegroundColor Green
Write-Host "請輸入您的 GitHub 倉庫 URL（例如：https://github.com/username/AI-Investment-Analyzer.git）：" -ForegroundColor Yellow
$repoUrl = Read-Host

git remote add origin $repoUrl
Write-Host "✅ GitHub 倉庫連接完成！" -ForegroundColor Green

# ==========================================
# 步驟 6：設置主分支
# ==========================================
Write-Host "`n步驟 6：設置主分支" -ForegroundColor Green
git branch -M main
Write-Host "✅ 主分支設置完成！" -ForegroundColor Green

# ==========================================
# 步驟 7：推送代碼到 GitHub
# ==========================================
Write-Host "`n步驟 7：推送代碼到 GitHub" -ForegroundColor Green
Write-Host "⚠️  接下來會要求您輸入 GitHub 用戶名和密碼（Personal Access Token）" -ForegroundColor Yellow
Write-Host "   用戶名：您的 GitHub 用戶名" -ForegroundColor Yellow
Write-Host "   密碼：您的 Personal Access Token（不是 GitHub 密碼）" -ForegroundColor Yellow
Write-Host "`n按 Enter 繼續..." -ForegroundColor Yellow
Read-Host

git push -u origin main

Write-Host "`n🎉 恭喜！代碼已成功上傳到 GitHub！" -ForegroundColor Green
Write-Host "請前往您的 GitHub 倉庫頁面確認：$repoUrl" -ForegroundColor Cyan
