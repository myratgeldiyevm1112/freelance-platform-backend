from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.review import LeaveReviewRequest, ReviewResponse
from app.application.use_cases.leave_review import LeaveReview
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.review_repository import ReviewRepository
from app.infrastructure.repositories.contract_repository import ContractRepository

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def leave_review(
    data: LeaveReviewRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    review_repo = ReviewRepository(db)
    contract_repo = ContractRepository(db)
    use_case = LeaveReview(review_repo, contract_repo)
    return await use_case.execute(data, current_user)

@router.get("/user/{user_id}", response_model=list[ReviewResponse])
async def get_user_reviews(
    user_id: UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ReviewRepository(db)
    reviews = await repo.get_by_reviewee_id(user_id)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.get("/user/{user_id}/rating")
async def get_user_rating(
    user_id: UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ReviewRepository(db)
    return await repo.get_average_rating(user_id)