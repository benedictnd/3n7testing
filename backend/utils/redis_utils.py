import json
from typing import Any, Optional, Union
import redis
from fastapi import Depends
from dependencies.database import get_redis

class RedisService:
    """
    Service for interacting with Redis
    """
    def __init__(self, redis_client: redis.Redis = Depends(get_redis)):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour default TTL

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis and deserialize from JSON
        """
        value = self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        Set a value in Redis with optional expiration time (in seconds)
        """
        try:
            serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
            return self.redis.set(key, serialized, ex=expire or self.default_ttl)
        except Exception as e:
            print(f"Error setting Redis key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> int:
        """
        Delete a key from Redis
        """
        return self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis
        """
        return bool(self.redis.exists(key))

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment a key's value
        """
        return self.redis.incr(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set an expiration time on a key
        """
        return self.redis.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """
        Get the remaining time to live of a key
        """
        return self.redis.ttl(key)

    async def publish(self, channel: str, message: Union[str, dict]) -> int:
        """
        Publish a message to a Redis channel
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        return self.redis.publish(channel, message)

    async def hset(self, name: str, key: str, value: Any) -> int:
        """
        Set a hash field to a value
        """
        serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
        return self.redis.hset(name, key, serialized)

    async def hget(self, name: str, key: str) -> Optional[Any]:
        """
        Get the value of a hash field
        """
        value = self.redis.hget(name, key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None 