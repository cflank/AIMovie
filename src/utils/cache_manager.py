import redis
import hashlib
import json
from typing import Any, Optional

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = {
            'video_analysis': 7 * 24 * 3600,    # 7天
            'speech_recognition': 30 * 24 * 3600, # 30天
            'narration': 24 * 3600,              # 1天
        }
    
    def _generate_key(self, content: Any, prefix: str) -> str:
        """生成缓存键"""
        content_hash = hashlib.md5(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()
        return f"{prefix}:{content_hash}"
    
    async def get_cached_result(self, content: Any, cache_type: str) -> Optional[Any]:
        """获取缓存结果"""
        key = self._generate_key(content, cache_type)
        cached = await self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_result(self, content: Any, result: Any, cache_type: str):
        """缓存结果"""
        key = self._generate_key(content, cache_type)
        ttl = self.cache_ttl.get(cache_type, 3600)
        await self.redis_client.setex(
            key, ttl, json.dumps(result, ensure_ascii=False)
        )