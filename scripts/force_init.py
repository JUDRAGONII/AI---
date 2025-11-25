"""
強制初始化資料庫
直接使用硬編碼配置，避開 .env 問題
"""
import sys
from pathlib import Path
import psycopg2
from loguru import logger

# 硬編碼資料庫配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 15432,
    'database': 'financial_data',
    'user': 'postgres',
    'password': '0824-003-a-8-Po'
}

def init_db():
    logger.info("🚀 開始強制初始化資料庫...")
    
    try:
        # 讀取 schema.sql
        schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # 連接資料庫
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 執行 Schema
        logger.info("執行 Schema SQL...")
        cur.execute(schema_sql)
        conn.commit()
        
        # 驗證表格
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        
        logger.success(f"✅ 資料庫初始化成功！共建立 {len(tables)} 個表格")
        for table in tables:
            logger.info(f"  - {table[0]}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ 初始化失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init_db()
