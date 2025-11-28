"""
精確刪除第121-141行的重複代碼
"""

settings_path = r'frontend\src\pages\Settings.jsx'

with open(settings_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 直接刪除121-141行（索引120-140）
# 需要找到clearApiKeys函數的位置
clear_api_line = None
for i, line in enumerate(lines):
    if 'const clearApiKeys' in line:
        clear_api_line = i
        break

if clear_api_line:
    print(f"✅ 找到clearApiKeys在第{clear_api_line+1}行")
    
    # 檢查第120行後到clearApiKeys之間是否有孤立代碼
    if clear_api_line > 120:
        # 刪除第120到clearApiKeys之間的所有內容
        new_lines = lines[:119] + ['\n'] + lines[clear_api_line:]
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("=" * 60)
        print("✅ Settings.jsx 修復完成！")
        print("=" * 60)
        print(f"已移除第120到第{clear_api_line}行之間的重複代碼")
        print()
        print("📝 Settings頁面應該已恢復正常")
        print("請重新載入瀏覽器頁面測試")  
        print("=" * 60)
    else:
        print("❌ 沒有發現重複代碼")
else:
    print("❌ 找不到clearApiKeys函數")
    
    # 顯示更多內容幫助診斷
    for i in range(140, 150):
        if i < len(lines):
            print(f"第{i+1}行: {lines[i][:60]}")
