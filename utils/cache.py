"""
API快取中介層
提供Redis快取功能，減少資料庫查詢負載
"""

import redis
import json
from functools import wraps
import hashlib
from datetime import timedelta


class APICache:
    """API快取管理器"""
    
    def __init__(self, host='localhost', port=6379, db=0, default_ttl=300):
        """
        初始化Redis連接
        
        Args:
            host: Redis主機
            port: Redis埠
            db: Redis資料庫編號
            default_ttl: 預設快取時間(秒)
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis快取已啟用")
        except redis.ConnectionError:
            self.enabled = False
            print("⚠️ Redis未啟動，快取功能已停用")
        
        self.default_ttl = default_ttl
    
    def generate_cache_key(self, prefix, *args, **kwargs):
        """生成快取鍵"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """獲取快取數據"""
        if not self.enabled:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"獲取快取錯誤: {e}")
            return None
    
    def set(self, key, value, ttl=None):
        """設置快取數據"""
        if not self.enabled:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value, ensure_ascii=False, default=str)
            )
            return True
        except Exception as e:
            print(f"設置快取錯誤: {e}")
            return False
    
    def delete(self, key):
        """刪除快取"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"刪除快取錯誤: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """清除符合模式的所有快取"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"清除快取錯誤: {e}")
            return False
    
    def cache_decorator(self, prefix, ttl=None):
        """
        快取裝飾器
        
        使用方式:
        @cache.cache_decorator('stock_prices', ttl=60)
        def get_stock_prices(code, days=30):
            # 函數邏輯
            return data
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成快取鍵
                cache_key = self.generate_cache_key(prefix, *args, **kwargs)
                
                # 嘗試從快取獲取
                cached_data = self.get(cache_key)
                if cached_data is not None:
                    print(f"🎯 快取命中: {cache_key[:16]}...")
                    return cached_data
                
                # 執行函數
                result = func(*args, **kwargs)
                
                # 儲存到快取
                if result is not None:
                    self.set(cache_key, result, ttl)
                    print(f"💾 快取已儲存: {cache_key[:16]}...")
                
                return result
            
            return wrapper
        return decorator


# 創建全域快取實例
cache = APICache(default_ttl=300)  # 預設5分鐘


# 使用範例
if __name__ == '__main__':
    print("=" * 60)
    print("🔧 API快取系統測試")
    print("=" * 60)
    
    # 測試快取功能
    @cache.cache_decorator('test_data', ttl=10)
    def get_test_data(param):
        print(f"📊 執行函數: param={param}")
        return {'data': f'result_{param}', 'timestamp': 'now'}
    
    # 第一次調用（執行函數）
    print("\n第一次調用:")
    result1 = get_test_data('abc')
    print(f"結果: {result1}")
    
    # 第二次調用（從快取獲取）
    print("\n第二次調用:")
    result2 = get_test_data('abc')
    print(f"結果: {result2}")
    
    # 不同參數（執行函數）
    print("\n不同參數:")
    result3 = get_test_data('xyz')
    print(f"結果: {result3}")
    
    print("\n" + "=" * 60)
    print("✅ 快取測試完成")
    print("=" * 60)
