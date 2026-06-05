import json
from redis.asyncio import Redis


class JobsCache:

    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, page: int, page_size: int, status: str | None,
              min_budget: float | None, max_budget: float | None) -> str:
        return f"jobs:page:{page}:size:{page_size}:status:{status}:min:{min_budget}:max:{max_budget}"

    async def get(self, page: int, page_size: int, status: str | None,
                  min_budget: float | None, max_budget: float | None) -> dict | None:
        key = self._key(page, page_size, status, min_budget, max_budget)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, page: int, page_size: int, status: str | None,
                min_budget: float | None, max_budget: float | None,
                value: dict) -> None:
        key = self._key(page, page_size, status, min_budget, max_budget)
        from pydantic import RootModel
        serialized = RootModel[dict](value).model_dump_json()
        await self.redis.set(key, serialized, ex=60)

    async def invalidate_all(self) -> None:
        keys = await self.redis.keys("jobs:*")
        if keys:
            await self.redis.delete(*keys)
