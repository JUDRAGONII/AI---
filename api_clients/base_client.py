"""
基礎 API 客戶端類別
提供：
- 請求頻率限制（rate limiting）
- 自動重試機制（exponential backoff）
- 錯誤處理與日誌記錄
- 響應快取
"""

import time
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
import hashlib
import json


class RateLimiter:
    """API 請求頻率限制器"""
    
    def __init__(self, delay: float = 1.0, daily_limit: Optional[int] = None):
        """
        Args:
            delay: 每次請求間隔秒數
            daily_limit: 每日請求次數上限（None 表示無限制）
        """
        self.delay = delay
        self.daily_limit = daily_limit
        self.last_request_time = 0
        self.daily_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def wait(self):
        """等待至可以發送下一個請求"""
        # 檢查是否需要重置每日計數
        if datetime.now() >= self.daily_reset_time:
            self.daily_count = 0
            self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # 檢查每日限制
        if self.daily_limit and self.daily_count >= self.daily_limit:
            wait_time = (self.daily_reset_time - datetime.now()).total_seconds()
            if wait_time > 0:
                logger.warning(f"已達每日請求上限 {self.daily_limit}，等待 {wait_time:.0f} 秒至明日重置")
                time.sleep(wait_time)
                self.daily_count = 0
        
        # 計算需要等待的時間
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            wait_time = self.delay - elapsed
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.daily_count += 1


class ResponseCache:
    """簡單的記憶體快取"""
    
    def __init__(self, ttl: int = 3600):
        """
        Args:
            ttl: 快取存活時間（秒）
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """取得快取資料"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """設定快取資料"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """清除所有快取"""
        self.cache.clear()


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"達到最大重試次數 {max_retries}，放棄請求")
                        raise
                    
                    wait_time = backoff_factor ** retries
                    logger.warning(f"請求失敗（{e}），{wait_time:.1f} 秒後重試（{retries}/{max_retries}）")
                    time.sleep(wait_time)
            
        return wrapper
    return decorator


class BaseAPIClient:
    """基礎 API 客戶端"""
    
    def __init__(
        self,
        api_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        rate_limit_delay: float = 1.0,
        daily_limit: Optional[int] = None,
        cache_ttl: int = 3600,
        timeout: int = 30
    ):
        """
        Args:
            api_name: API 名稱（用於日誌）
            api_key: API 金鑰
            base_url: API 基礎 URL
            rate_limit_delay: 請求間隔秒數
            daily_limit: 每日請求上限
            cache_ttl: 快取存活時間（秒）
            timeout: 請求逾時時間（秒）
        """
        self.api_name = api_name
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        
        # 初始化元件
        self.rate_limiter = RateLimiter(delay=rate_limit_delay, daily_limit=daily_limit)
        self.cache = ResponseCache(ttl=cache_ttl)
        self.session = requests.Session()
        
        logger.info(f"初始化 {api_name} API 客戶端")
        logger.debug(f"  請求間隔: {rate_limit_delay} 秒")
        logger.debug(f"  每日限制: {daily_limit if daily_limit else '無限制'}")
        logger.debug(f"  快取時效: {cache_ttl} 秒")
    
    def _generate_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """生成快取鍵值"""
        key_data = f"{url}_{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        執行 HTTP 請求
        
        Args:
            method: HTTP 方法（GET, POST 等）
            url: 請求 URL
            params: 查詢參數
            headers: 請求標頭
            use_cache: 是否使用快取
        
        Returns:
            回應資料（JSON）
        """
        # 檢查快取
        if use_cache and method.upper() == 'GET':
            cache_key = self._generate_cache_key(url, params)
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"[{self.api_name}] 使用快取資料: {url}")
                return cached_data
        
        # 等待限流
        self.rate_limiter.wait()
        
        # 準備請求
        if headers is None:
            headers = {}
        
        # 添加 API 金鑰（如果需要）
        if self.api_key:
            # 不同 API 的金鑰傳遞方式不同，子類別應覆寫此方法
            params = params or {}
            params['apikey'] = self.api_key
        
        # 發送請求
        logger.debug(f"[{self.api_name}] 請求: {method} {url}")
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            timeout=self.timeout
        )
        
        # 檢查回應狀態
        response.raise_for_status()
        
        # 解析 JSON
        data = response.json()
        
        # 儲存快取
        if use_cache and method.upper() == 'GET':
            cache_key = self._generate_cache_key(url, params)
            self.cache.set(cache_key, data)
        
        logger.debug(f"[{self.api_name}] 請求成功")
        
        return data
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET 請求"""
        return self._make_request('GET', url, params=params, **kwargs)
    
    def post(self, url: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST 請求"""
        return self._make_request('POST', url, params=params, use_cache=False, **kwargs)
    
    def close(self):
        """關閉 Session"""
        self.session.close()
        logger.info(f"[{self.api_name}] 關閉連線")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
