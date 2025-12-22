from datetime import datetime, timedelta
from functools import lru_cache
import time


class CachedService:
    def __init__(self, cache_ttl=300):
        self._cache = {}
        self._cache_ttl = cache_ttl
    
    def _get_cached(self, key):
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return data
            del self._cache[key]
        return None
    
    def _set_cache(self, key, data):
        self._cache[key] = (data, datetime.now())
    
    def _invalidate_cache(self, pattern=None):
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()


class RetryableMixin:
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _retry_request(self, request_func, operation_name="operation"):
        for attempt in range(self.max_retries):
            try:
                return request_func()
            except Exception as error:
                should_retry = attempt < self.max_retries - 1
                
                if should_retry:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"Error on {operation_name} (attempt {attempt + 1}/{self.max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"Final error on {operation_name}: {error}")
                    return None
        return None


class BaseService(CachedService, RetryableMixin):
    def __init__(self, cache_ttl=300, max_retries=3, retry_delay=1):
        CachedService.__init__(self, cache_ttl)
        RetryableMixin.__init__(self, max_retries, retry_delay)