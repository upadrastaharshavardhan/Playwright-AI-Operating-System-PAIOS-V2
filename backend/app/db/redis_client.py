import redis.asyncio as redis
from app.core.config import get_settings
from app.core.logging import logger
import json

settings = get_settings()


class RedisClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if self._client is None:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._client.ping()
            logger.info("Redis connection established")

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed")

    async def set(self, key: str, value, expire: int = None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self._client.set(key, value, ex=expire)

    async def get(self, key: str):
        value = await self._client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def delete(self, key: str):
        await self._client.delete(key)

    async def publish(self, channel: str, message: dict):
        await self._client.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
