import json
from datetime import timedelta
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

from core.config import settings

redis = Redis.from_url(settings.redis_url, decode_responses=True)


class RedisCache:
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        data = await redis.get(key)
        return json.loads(data) if data else None

    @staticmethod
    async def set(key: str, value: Any, expire: Optional[timedelta] = None) -> None:
        json_value = json.dumps(jsonable_encoder(value))
        if expire:
            await redis.setex(key, expire, json_value)
        else:
            await redis.set(key, json_value)

    @staticmethod
    async def delete(key: str) -> None:
        await redis.delete(key)
