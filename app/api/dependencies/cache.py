from redis.asyncio import Redis
from app.infrastructure.cache.redis_client import get_redis_client


async def get_redis() -> Redis:
    return await get_redis_client()
