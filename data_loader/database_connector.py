"""
資料庫連接器模組

提供PostgreSQL資料庫的連接管理、查詢執行和CRUD操作
"""
import os
import psycopg2
from psycopg2 import pool, extras
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from dotenv import load_dotenv
from contextlib import contextmanager

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))


class DatabaseConnector:
    """PostgreSQL資料庫連接器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化資料庫連接器
        
        Args:
            config: 資料庫配置字典，若為None則從環境變數讀取
        """
        if config is None:
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '15432')),
                'database': os.getenv('DB_NAME', 'financial_data'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'your_password_here')
            }
        
        self.config = config
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化連接池"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info(f"✅ 資料庫連接池初始化成功：{self.config['database']}@{self.config['host']}:{self.config['port']}")
        except Exception as e:
            logger.error(f"❌ 資料庫連接池初始化失敗：{e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        獲取資料庫連接（上下文管理器）
        
        Yields:
            connection: 資料庫連接對象
        """
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            logger.error(f"❌ 獲取連接失敗：{e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def test_connection(self) -> bool:
        """
        測試資料庫連接
        
        Returns:
            bool: 連接成功返回True，否則False
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        logger.info("✅ 資料庫連接測試成功")
                        return True
            return False
        Args:
            table: 表格名稱
            data: 要插入的資料字典
            returning: 返回的欄位名稱
        
        Returns:
            插入記錄的ID（若有returning）
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())
            
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
            """
            
            if returning:
                query += f" RETURNING {returning}"
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    
                    if returning:
                        result = cursor.fetchone()
                        return result[0] if result else None
                    return None
        except Exception as e:
            logger.error(f"❌ 插入失敗：{e}\nTable: {table}\nData: {data}")
            raise
    
    def execute_update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        執行UPDATE操作
        
        Args:
            table: 表格名稱
            data: 要更新的資料字典
            where: WHERE條件字典
        
        Returns:
            更新的記錄數
        """
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
            values = tuple(data.values()) + tuple(where.values())
            
            query = f"""
                UPDATE {table}
                SET {set_clause}
                WHERE {where_clause}
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ 更新失敗：{e}\nTable: {table}\nData: {data}\nWhere: {where}")
            raise
    
    def execute_delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        執行DELETE操作
        
        Args:
            table: 表格名稱
            where: WHERE條件字典
        
        Returns:
            刪除的記錄數
        """
        try:
            where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
            values = tuple(where.values())
            
            query = f"""
                DELETE FROM {table}
                WHERE {where_clause}
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ 刪除失敗：{e}\nTable: {table}\nWhere: {where}")
            raise
    
    def execute_batch(
        self,
        query: str,
        data_list: List[Tuple]
    ) -> bool:
        """
        執行批次操作
        
        Args:
            query: SQL語句
            data_list: 資料列表
        
        Returns:
            bool: 成功返回True
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    extras.execute_batch(cursor, query, data_list)
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"❌ 批次操作失敗：{e}\nQuery: {query}")
            raise
    
    def bulk_insert(
        self,
        table: str,
        data_list: List[Dict[str, Any]]
    ) -> int:
        """
        批次插入資料
        
        Args:
            table: 表格名稱
            data_list: 資料字典列表
        
        Returns:
            插入的記錄數
        """
        if not data_list:
            return 0
        
        try:
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(data_list[0]))
            
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
            """
            
            values_list = [tuple(d.values()) for d in data_list]
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    extras.execute_batch(cursor, query, values_list)
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ 批次插入失敗：{e}\nTable: {table}")
            raise
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        獲取表格Schema
        
        Args:
            table_name: 表格名稱
        
        Returns:
            Schema資訊列表
        """
        query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute_query(query, (table_name,))
    
    def execute_raw(self, sql: str, params: Tuple = None) -> Any:
        """
        執行原始SQL語句
        
        Args:
            sql: SQL語句
            params: 參數
        
        Returns:
            執行結果
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()
                    
                    try:
                        return cursor.fetchall()
                    except:
                        return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ SQL執行失敗：{e}\nSQL: {sql}")
            raise
    
    def close(self):
        """關閉連接池"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ 資料庫連接池已關閉")


# 測試代碼
if __name__ == '__main__':
    # 初始化
    db = DatabaseConnector()
    
    # 測試連接
    if db.test_connection():
        print("✅ 資料庫連接測試成功")
        
        # 測試查詢
        try:
            result = db.execute_query("SELECT version()")
            print(f"資料庫版本：{result[0]['version']}")
            
            # 測試表格查詢
            tables = db.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            print(f"\n找到 {len(tables)} 個表格：")
            for table in tables[:5]:
                print(f"  - {table['table_name']}")
            
        except Exception as e:
            print(f"❌ 測試失敗：{e}")
    
    # 關閉
    db.close()
