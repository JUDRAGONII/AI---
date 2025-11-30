import os
from dotenv import load_dotenv

# 測試環境變數加載
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
print(f"Loading .env from: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

load_dotenv(env_path)

key = os.getenv('GOOGLE_AI_API_KEY')
if key:
    print(f"\n✓ GOOGLE_AI_API_KEY found!")
    print(f"  Length: {len(key)} characters")
    print(f"  Preview: {key[:10]}...{key[-5:]}")
else:
    print("\n✗ GOOGLE_AI_API_KEY not found")
    print("\nChecking file content...")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GOOGLE_AI_API_KEY' in content:
                print("  - String 'GOOGLE_AI_API_KEY' found in file")
                # 找到該行
                for line in content.split('\n'):
                    if 'GOOGLE_AI_API_KEY' in line and not line.strip().startswith('#'):
                        print(f"  - Line: {line[:50]}...")
            else:
                print("  - String 'GOOGLE_AI_API_KEY' NOT found in file")
                print("\n  Available variables in .env:")
                for line in content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        var_name = line.split('=')[0].strip()
                        print(f"    - {var_name}")
    except Exception as e:
        print(f"Error reading file: {e}")
