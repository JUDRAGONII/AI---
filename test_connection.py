"""
簡單的資料庫連線測試
"""
import psycopg2

# 測試連線參數
config = {
    'host': 'localhost',
    'port': 15432,
    'database': 'financial_data',
    'user': 'postgres',
    'password': '0824-003-a-8-Po'
}

try:
    print(f"嘗試連線到 PostgreSQL...")
    print(f"    Host: {config['host']}")
    print(f"    Port: {config['port']}")
    print(f"    Database: {config['database']}")
    print(f"    User: {config['user']}")
    
    conn = psycopg2.connect(**config)
    cur = conn.cursor()
    
    print("\n✅ 資料庫連線成功！\n")
    
    # 測試查詢
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"PostgreSQL 版本：{version}\n")
    
    # 列出所有表格
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    
    tables = cur.fetchall()
    if tables:
        print(f"已存在的表格數：{len(tables)}")
        for table in tables[:5]:
            print(f"  - {table[0]}")
        if len(tables) > 5:
            print(f"  ... 還有 {len(tables) - 5} 個表格")
    else:
        print("尚未建立表格（需要執行 schema.sql）")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 連線失敗：{e}\n")
    print("請檢查：")
    print("  1. Docker 容器是否運行：docker ps")
    print("  2. 端口是否正確：15432")
    print("  3. 密碼是否正確：docker-compose.yml 中的 DB_PASSWORD")
