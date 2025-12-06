
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

def check_schema():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ai_reports'
    """)
    
    columns = cursor.fetchall()
    print("ai_reports columns:")
    for col in columns:
        print(f"- {col[0]} ({col[1]})")
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_schema()
