"""
資料庫統計報告生成腳本
"""
import psycopg2
from datetime import datetime

def generate_db_stats():
    conn = psycopg2.connect(
        host='localhost',
        port=15432,
        database='quant_db',
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    
    print("="*70)
    print(f"📊 資料庫統計報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 1. 表格清單與記錄數
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        ORDER BY table_name
    """)
    tables = [t[0] for t in cur.fetchall()]
    
    print(f"\n📋 資料庫表格清單 (總共 {len(tables)} 個)")
    print("-"*70)
    for table in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cur.fetchone()[0]
        print(f"  {table:<30} {count:>10,} 筆")
    
    # 2. 股價數據統計
    print("\n" + "="*70)
    print("📈 股價數據統計")
    print("-"*70)
    
    cur.execute("""
        SELECT stock_code, COUNT(*) as days, 
               MIN(trade_date) as start_date, 
               MAX(trade_date) as end_date
        FROM tw_stock_prices 
        GROUP BY stock_code 
        ORDER BY days DESC 
        LIMIT 10
    """)
    print("\n台股價格數據覆蓋（Top 10）:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]:,}天 ({row[2]} ~ {row[3]})")
    
    # 3. AI報告統計
    print("\n" + "="*70)
    print("🤖 AI報告統計")
    print("-"*70)
    
    cur.execute("""
        SELECT report_type, COUNT(*) as count,
               MIN(created_at)::date as first_report,
               MAX(created_at)::date as last_report
        FROM ai_reports 
        GROUP BY report_type
    """)
    print("\nAI報告分類統計:")
    for row in cur.fetchall():
        print(f"  {row[0]:<25} {row[1]:>5}份 ({row[2]} ~ {row[3]})")
    
    # 4. 投資組合統計
    print("\n" + "="*70)
    print("💼 投資組合統計")
    print("-"*70)
    
    cur.execute("SELECT COUNT(*) FROM user_portfolios")
    portfolio_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cur.fetchone()[0]
    
    print(f"\n  持倉記錄: {portfolio_count:,} 筆")
    print(f"  交易記錄: {transaction_count:,} 筆")
    
    # 5. 籌碼分析統計
    print("\n" + "="*70)
    print("💰 籌碼分析統計")
    print("-"*70)
    
    cur.execute("SELECT COUNT(*) FROM institutional_trades")
    inst_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM margin_trading")
    margin_count = cur.fetchone()[0]
    
    print(f"\n  三大法人記錄: {inst_count:,} 筆")
    print(f"  融資融券記錄: {margin_count:,} 筆")
    
    # 6. 技術指標統計
    print("\n" + "="*70)
    print("📊 技術指標統計")
    print("-"*70)
    
    cur.execute("SELECT COUNT(*) FROM technical_indicators")
    indicator_count = cur.fetchone()[0]
    print(f"\n  技術指標記錄: {indicator_count:,} 筆")
    
    print("\n" + "="*70)
    print("✅ 統計報告生成完成")
    print("="*70)
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    try:
        generate_db_stats()
    except Exception as e:
        print(f"錯誤: {str(e)}")
