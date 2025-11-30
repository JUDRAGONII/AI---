import os
from dotenv import load_dotenv

def check_env():
    env_path = os.path.join(os.getcwd(), 'config', '.env')
    print(f"Checking .env at: {env_path}")
    
    if os.path.exists(env_path):
        print(".env file exists")
        load_dotenv(env_path)
        key = os.getenv('GOOGLE_AI_API_KEY')
        if key:
            print(f"GOOGLE_AI_API_KEY found: {key[:5]}...")
        else:
            print("GOOGLE_AI_API_KEY not found in environment variables")
            
            # 讀取文件內容檢查變數名
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'GOOGLE_AI_API_KEY' in content:
                    print("GOOGLE_AI_API_KEY string found in file content")
                else:
                    print("GOOGLE_AI_API_KEY string NOT found in file content")
    else:
        print(".env file does NOT exist")

if __name__ == "__main__":
    check_env()
