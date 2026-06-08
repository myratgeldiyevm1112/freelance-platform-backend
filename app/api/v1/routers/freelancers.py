import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.user import FreelancerPublicProfile
from app.application.use_cases.search_freelancers import SearchFreelancers
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.exceptions import NotFoundError

router = APIRouter(prefix="/freelancers", tags=["Freelancers"])


@router.get("/", response_model=list[FreelancerPublicProfile])
async def search_freelancers(
    skill: str | None = Query(None, description="Filter by skill e.g. python"),
    min_rate: float | None = Query(None, ge=0, description="Minimum hourly rate"),
    max_rate: float | None = Query(None, ge=0, description="Maximum hourly rate"),
    min_rating: float | None = Query(None, ge=0, le=5, description="Minimum rating"),
    q: str | None = Query(None, description="Search by name or bio"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = SearchFreelancers(UserRepository(db))
    return await use_case.execute(
        skill=skill,
        min_rate=min_rate,
        max_rate=max_rate,
        min_rating=min_rating,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{freelancer_id}", response_model=FreelancerPublicProfile)
async def get_freelancer_profile(
    freelancer_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    freelancer = await repo.get_by_id(freelancer_id)
    if not freelancer:
        raise NotFoundError("Freelancer not found")
    return FreelancerPublicProfile(
        id=freelancer.id,
        full_name=freelancer.full_name,
        bio=freelancer.bio,
        hourly_rate=freelancer.hourly_rate,
        avatar_url=freelancer.avatar_url,
        portfolio_urls=freelancer.portfolio_urls,
    )
