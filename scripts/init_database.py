"""
資料庫初始化腳本
執行此腳本將：
1. 測試資料庫連線
2. 執行 schema.sql 建立所有表格
3. 驗證表格建立成功
4. 插入初始配置資料
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
from loguru import logger

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_CONFIG

# 配置日誌
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add("logs/init_database.log", rotation="10 MB")


def test_connection():
    """測試資料庫連線"""
    logger.info("🔍 測試資料庫連線...")
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.success(f"✅ 資料庫連線成功！")
        logger.info(f"   PostgreSQL 版本: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ 資料庫連線失敗: {e}")
        return False


def execute_schema():
    """執行 schema.sql 建立所有表格"""
    logger.info("📝 執行 schema.sql...")
    
    schema_file = Path(__file__).parent.parent / 'database' / 'schema.sql'
    
    if not schema_file.exists():
        logger.error(f"❌ 找不到 schema.sql 檔案: {schema_file}")
        return False
    
    try:
        # 讀取 SQL 檔案
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # 執行 SQL
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        logger.info("   執行 SQL 指令...")
        cursor.execute(schema_sql)
        conn.commit()
        
        logger.success("✅ Schema 執行成功！")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema 執行失敗: {e}")
        return False


def verify_tables():
    """驗證表格建立成功"""
    logger.info("🔎 驗證表格建立狀態...")
    
    expected_tables = [
        # 原始資料層
        'tw_stock_info', 'tw_stock_prices',
        'us_stock_info', 'us_stock_prices',
        'gold_prices', 'exchange_rates',
        'macro_indicators', 'financial_news',
        # 預計算層
        'technical_indicators', 'quant_scores',
        # AI 快取層
        'ai_reports', 'similarity_matrix',
        # 進階分析層
        'shareholder_dispersion', 'institutional_holdings_13f',
        'portfolio_performance', 'backtest_results',
        'behavioral_metrics', 'stress_test_results',
        # 系統管理層
        'sync_status', 'system_config'
    ]
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # 查詢所有表格
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        actual_tables = [row[0] for row in cursor.fetchall()]
        
        # 檢查每個預期的表格
        missing_tables = []
        found_tables = []
        
        for table in expected_tables:
            if table in actual_tables:
                found_tables.append(table)
            else:
                missing_tables.append(table)
        
        # 輸出結果
        logger.info(f"   預期表格數：{len(expected_tables)}")
        logger.info(f"   實際建立數：{len(found_tables)}")
        
        if missing_tables:
            logger.warning(f"⚠️  缺少表格 ({len(missing_tables)}):")
            for table in missing_tables:
                logger.warning(f"      - {table}")
        
        if found_tables:
            logger.success(f"✅ 成功建立 {len(found_tables)} 個表格：")
            
            # 分類顯示
            categories = {
                '原始資料層': ['tw_stock_info', 'tw_stock_prices', 'us_stock_info', 'us_stock_prices', 
                              'gold_prices', 'exchange_rates', 'macro_indicators', 'financial_news'],
                '預計算層': ['technical_indicators', 'quant_scores'],
                'AI 快取層': ['ai_reports', 'similarity_matrix'],
                '進階分析層': ['shareholder_dispersion', 'institutional_holdings_13f', 
                              'portfolio_performance', 'backtest_results', 
                              'behavioral_metrics', 'stress_test_results'],
                '系統管理層': ['sync_status', 'system_config']
            }
            
            for category, tables in categories.items():
                category_tables = [t for t in tables if t in found_tables]
                if category_tables:
                    logger.info(f"   📊 {category}: {len(category_tables)} 個")
        
        # 查詢視圖
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        views = [row[0] for row in cursor.fetchall()]
        if views:
            logger.info(f"   👁️  視圖: {len(views)} 個 ({', '.join(views)})")
        
        cursor.close()
        conn.close()
        
        return len(missing_tables) == 0
        
    except Exception as e:
        logger.error(f"❌ 驗證表格失敗: {e}")
        return False


def check_indexes():
    """檢查索引建立狀況"""
    logger.info("🔍 檢查索引建立狀況...")
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        logger.success(f"✅ 成功建立 {len(indexes)} 個索引")
        
        # 統計每個表格的索引數量
        from collections import defaultdict
        table_indexes = defaultdict(int)
        for _, table, _ in indexes:
            table_indexes[table] += 1
        
        logger.info("   主要表格索引統計：")
        for table in ['tw_stock_prices', 'us_stock_prices', 'technical_indicators', 'quant_scores']:
            count = table_indexes.get(table, 0)
            logger.info(f"      {table}: {count} 個索引")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 檢查索引失敗: {e}")
        return False


def insert_sample_config():
    """插入範例配置資料"""
    logger.info("📝 插入範例配置資料...")
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # 檢查是否已有資料
        cursor.execute("SELECT COUNT(*) FROM system_config;")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"   已有 {count} 筆配置資料，跳過插入")
        else:
            logger.info("   插入預設配置...")
            # 配置已在 schema.sql 中定義，此處不需額外插入
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 插入配置失敗: {e}")
        return False


def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("🚀 開始初始化專業金融資料庫")
    logger.info("=" * 60)
    
    # 步驟 1: 測試連線
    if not test_connection():
        logger.error("❌ 初始化失敗：無法連線資料庫")
        logger.info("   請檢查：")
        logger.info("   1. Docker 容器是否正在運行？")
        logger.info("   2. .env 檔案中的資料庫設定是否正確？")
        logger.info("   3. 資料庫密碼是否正確？")
        return False
    
    # 步驟 2: 執行 Schema
    if not execute_schema():
        logger.error("❌ 初始化失敗：無法執行 schema.sql")
        return False
    
    # 步驟 3: 驗證表格
    if not verify_tables():
        logger.warning("⚠️  部分表格建立失敗，但繼續執行...")
    
    # 步驟 4: 檢查索引
    check_indexes()
    
    # 步驟 5: 插入配置
    insert_sample_config()
    
    logger.info("=" * 60)
    logger.success("🎉 資料庫初始化完成！")
    logger.info("=" * 60)
    logger.info("📊 下一步：")
    logger.info("   1. 安裝 Python 依賴：pip install -r requirements.txt")
    logger.info("   2. 配置 API 金鑰：複製 config/.env.example 為 .env 並填入金鑰")
    logger.info("   3. 開始資料回溯：python scripts/run_backfill.py --phase 1")
    logger.info("=" * 60)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
