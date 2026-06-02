import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.review import ReviewEntity
from app.infrastructure.database.models.review import Review

class ReviewRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Review) -> ReviewEntity:
        return ReviewEntity(
            id=model.id,
            contract_id=model.contract_id,
            reviewer_id=model.reviewer_id,
            reviewee_id=model.reviewee_id,
            rating=model.rating,
            comment=model.comment,
            created_at=model.created_at,
        )

    async def create(self, entity: ReviewEntity) -> ReviewEntity:
        review = Review(
            id=entity.id,
            contract_id=entity.contract_id,
            reviewer_id=entity.reviewer_id,
            reviewee_id=entity.reviewee_id,
            rating=entity.rating,
            comment=entity.comment,
        )
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return self._to_entity(review)

    async def get_by_contract_id(self, contract_id: uuid.UUID) -> ReviewEntity | None:
        result = await self.session.execute(
            select(Review).where(Review.contract_id == contract_id)
        )
        review = result.scalar_one_or_none()
        return self._to_entity(review) if review else None

    async def get_by_reviewee_id(self, reviewee_id: uuid.UUID) -> list[ReviewEntity]:
        result = await self.session.execute(
            select(Review).where(Review.reviewee_id == reviewee_id)
        )
        return [self._to_entity(r) for r in result.scalars().all()]
