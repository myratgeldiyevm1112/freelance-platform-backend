from app.application.interfaces.user_repository import IUserRepository
from app.domain.entities.user import UserEntity


class SearchFreelancers:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(
        self,
        skill: str | None = None,
        min_rate: float | None = None,
        max_rate: float | None = None,
        min_rating: float | None = None,
        q: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[UserEntity]:
        return await self.user_repo.search_freelancers(
            skill=skill,
            min_rate=min_rate,
            max_rate=max_rate,
            min_rating=min_rating,
            q=q,
            limit=limit,
            offset=offset,
        )
