from redis.asyncio import Redis
from app.core.config import settings


class TokenStore:

    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, user_id: str) -> str:
        return f"refresh_token:{user_id}"

    async def save(self, user_id: str, token: str) -> None:
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await self.redis.set(self._key(user_id), token, ex=ttl)

    async def get(self, user_id: str) -> str | None:
        return await self.redis.get(self._key(user_id))

    async def delete(self, user_id: str) -> None:
        await self.redis.delete(self._key(user_id))
