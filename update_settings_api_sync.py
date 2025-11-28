"""
簡化版：直接讀取並精確替換Settings.jsx中的saveApiKeys函數
"""

# 讀取檔案
settings_path = r'frontend\src\pages\Settings.jsx'

with open(settings_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 尋找saveApiKeys函數的開始和結束位置
start_line = None
end_line = None
bracket_count = 0
found_function = False

for i, line in enumerate(lines):
    if 'const saveApiKeys = async () =>' in line:
        start_line = i
        found_function = True
        bracket_count = 0
        continue
    
    if found_function:
        # 計算大括號
        bracket_count += line.count('{') - line.count('}')
        if bracket_count == 0 and '}' in line:
            end_line = i
            break

if start_line is None or end_line is None:
    print("❌ 無法找到saveApiKeys函數")
    print(f"start_line: {start_line}, end_line: {end_line}")
    exit(1)

print(f"✅ 找到函數：行 {start_line+1} 到 {end_line+1}")

# 新的函數內容
new_function_lines = '''    const saveApiKeys = async () => {
        // 儲存到localStorage
        localStorage.setItem('apiKeys', JSON.stringify(apiKeys))
        setSyncStatus({ syncing: true, message: '正在儲存並同步...', type: 'info' })
        
        try {
            // 同步到後端（包括共用和後端專用的API金鑰）
            const response = await fetch('http://localhost:5000/api/config/sync-api-keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(apiKeys)
            })
            
            const result = await response.json()
            
            if (result.success) {
                setSyncStatus({ 
                    syncing: false, 
                    message: `✅ ${result.message}（${result.synced_keys.length}個金鑰）`, 
                    type: 'success' 
                })
            } else {
                setSyncStatus({ 
                    syncing: false, 
                    message: `⚠️ 已儲存到前端，但後端同步失敗: ${result.message}`, 
                    type: 'warning' 
                })
            }
        } catch (error) {
            console.error('後端同步錯誤:', error)
            setSyncStatus({ 
                syncing: false, 
                message: '✅ 已儲存到前端（後端API未連接）', 
                type: 'success' 
            })
        }
        
        // 3秒後清除訊息
        setTimeout(() => setSyncStatus({ syncing: false, message: '', type: '' }), 3000)
    }
'''

# 組合新內容
new_lines = lines[:start_line] + [new_function_lines + '\n'] + lines[end_line+1:]

# 寫回檔案
with open(settings_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("=" * 60)
print("✅ Settings.jsx 修改完成！")
print("=" * 60)
print(f"修改範圍：第 {start_line+1} 行到第 {end_line+1} 行")
print()
print("✨ 已添加功能：")
print("   1. 後端API同步呼叫")
print("   2. 完整錯誤處理")
print("   3. 同步狀態訊息顯示")
print()
print("📝 測試步驟：")
print("   1. 前往 http://localhost:5173/settings")
print("   2. 填寫任意API金鑰（例如：test_key_12345）")
print("   3. 點擊儲存按鈕")
print("   4. 查看是否顯示「成功同步」訊息")
print("=" * 60)
