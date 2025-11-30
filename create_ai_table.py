import psycopg2
import os

def create_table():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=15432,
            database='quant_db',
            user='postgres',
            password='postgres'
        )
        cur = conn.cursor()
        
        # 創建 ai_analysis_reports 表
        create_sql = """
        CREATE TABLE IF NOT EXISTS ai_analysis_reports (
            id SERIAL PRIMARY KEY,
            report_type VARCHAR(50) NOT NULL, -- market, stock, portfolio
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            sentiment VARCHAR(20), -- bullish, bearish, neutral
            accuracy DECIMAL(5, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 創建索引
        CREATE INDEX IF NOT EXISTS idx_ai_reports_type ON ai_analysis_reports(report_type);
        CREATE INDEX IF NOT EXISTS idx_ai_reports_date ON ai_analysis_reports(created_at);
        """
        
        cur.execute(create_sql)
        conn.commit()
        print("Table 'ai_analysis_reports' created successfully!")
        
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    create_table()
