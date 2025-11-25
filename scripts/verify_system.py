"""
系統驗證腳本
檢查所有核心元件是否正常
"""

import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """檢查檔案是否存在"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 缺失: {filepath}")
        return False

def main():
    print("=" * 60)
    print("🔍 專業金融資料庫系統驗證")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    
    # 1. 檢查核心配置檔案
    print("\n【1/6】檢查核心配置檔案...")
    files_to_check = [
        (base_dir / "docker-compose.yml", "Docker Compose 配置"),
        (base_dir / "requirements.txt", "Python 依賴清單"),
        (base_dir / ".gitignore", "Git 忽略檔案"),
        (base_dir / "config" / "settings.py", "系統配置"),
        (base_dir / "config" / ".env.example", "環境變數範例"),
    ]
    
    config_ok = all(check_file_exists(f, d) for f, d in files_to_check)
    
    # 2. 檢查資料庫架構
    print("\n【2/6】檢查資料庫架構...")
    schema_ok = check_file_exists(
        base_dir / "database" / "schema.sql",
        "資料庫 Schema"
    )
    
    # 3. 檢查 API 客戶端
    print("\n【3/6】檢查 API 客戶端模組...")
    api_clients = [
        ("base_client.py", "基礎客戶端"),
        ("tw_stock_client.py", "台股客戶端"),
        ("us_stock_client.py", "美股客戶端"),
        ("gold_client.py", "黃金價格客戶端"),
        ("exchange_rate_client.py", "匯率客戶端"),
        ("macro_client.py", "宏觀經濟客戶端"),
        ("news_client.py", "金融新聞客戶端"),
    ]
    
    api_ok = all(
        check_file_exists(base_dir / "api_clients" / f, d)
        for f, d in api_clients
    )
    
    # 4. 檢查資料處理模組
    print("\n【4/6】檢查資料處理模組...")
    data_loaders = [
        ("database_writer.py", "資料庫寫入器"),
    ]
    
    loader_ok = all(
        check_file_exists(base_dir / "data_loader" / f, d)
        for f, d in data_loaders
    )
    
    # 5. 檢查腳本
    print("\n【5/6】檢查執行腳本...")
    scripts = [
        ("init_database.py", "資料庫初始化"),
        ("run_backfill.py", "資料回溯"),
    ]
    
    scripts_ok = all(
        check_file_exists(base_dir / "scripts" / f, d)
        for f, d in scripts
    )
    
    # 6. 檢查文件
    print("\n【6/6】檢查文件...")
    docs = [
        ("README.md", "專案說明"),
        ("QUICKSTART.md", "快速啟動指南"),
        ("開發總結.md", "開發總結"),
    ]
    
    docs_ok = all(
        check_file_exists(base_dir / f, d)
        for f, d in docs
    )
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 驗證結果總結")
    print("=" * 60)
    
    all_ok = all([config_ok, schema_ok, api_ok, loader_ok, scripts_ok, docs_ok])
    
    if all_ok:
        print("✅ 所有核心元件驗證通過！")
        print("\n🚀 系統已就緒，可以開始使用：")
        print("   1. docker-compose up -d")
        print("   2. pip install -r requirements.txt")
        print("   3. python scripts/init_database.py")
        print("   4. python scripts/run_backfill.py --mode test")
        return 0
    else:
        print("❌ 部分元件缺失，請檢查上述輸出")
        return 1

if __name__ == '__main__':
    sys.exit(main())
