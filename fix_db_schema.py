
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

def fix_schema():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    cursor = conn.cursor()
    
    # 檢查 report_title 是否存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'ai_reports' AND column_name = 'report_title'
    """)
    
    if not cursor.fetchone():
        print("添加 report_title 欄位...")
        cursor.execute("ALTER TABLE ai_reports ADD COLUMN report_title VARCHAR(200)")
        conn.commit()
    else:
        print("report_title 欄位已存在")
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    fix_schema()
