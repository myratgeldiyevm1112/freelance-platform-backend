import json
from uuid import UUID
from redis.asyncio import Redis


class RatingCache:

    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, user_id: UUID) -> str:
        return f"rating:{user_id}"

    async def get(self, user_id: UUID) -> dict | None:
        data = await self.redis.get(self._key(user_id))
        return json.loads(data) if data else None

    async def set(self, user_id: UUID, value: dict) -> None:
        await self.redis.set(self._key(user_id), json.dumps(value), ex=300)

    async def invalidate(self, user_id: UUID) -> None:
        await self.redis.delete(self._key(user_id))
