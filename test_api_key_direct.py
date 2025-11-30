"""
直接測試 Gemini API Key 有效性
"""
import os
from dotenv import load_dotenv

# 載入環境變數
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)

# 讀取 API Key
api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')

print("="*60)
print("API Key 診斷測試")
print("="*60)

if not api_key:
    print("✗ 未找到 API Key")
    print("\n請檢查 config/.env 文件中是否包含:")
    print("  GEMINI_API_KEY=your_key 或")
    print("  GOOGLE_AI_API_KEY=your_key")
else:
    print(f"✓ 找到 API Key")
    print(f"  長度: {len(api_key)} 字符")
    print(f"  開頭: {api_key[:10]}...")
    print(f"  結尾: ...{api_key[-5:]}")
    
    # 檢查格式
    if api_key.startswith('AIzaSy'):
        print("  ✓ 格式看起來正確 (以 AIzaSy 開頭)")
    else:
        print(f"  ⚠ 格式可能有問題 (應以 AIzaSy 開頭，實際: {api_key[:6]}...)")
    
    # 嘗試實際調用
    print("\n嘗試調用 Gemini API...")
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        response = model.generate_content("請簡短回覆：測試成功")
        print(f"✓ API 調用成功！")
        print(f"  AI 回應: {response.text}")
        
    except Exception as e:
        print(f"✗ API 調用失敗")
        print(f"  錯誤: {str(e)[:200]}")
        
        if "API_KEY_INVALID" in str(e):
            print("\n原因分析：")
            print("  - API Key 本身無效")
            print("  - 可能是複製時有誤")
            print("  - 可能已過期或被撤銷")
            print("\n建議：")
            print("  1. 前往 https://makersuite.google.com/app/apikey")
            print("  2. 重新生成一個新的 API Key")
            print("  3. 確保啟用了 Generative Language API")

print("="*60)
