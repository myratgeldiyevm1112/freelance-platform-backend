import uuid
from app.application.dto.review import LeaveReviewRequest, ReviewResponse
from app.application.interfaces.review_repository import IReviewRepository
from app.application.interfaces.contract_repository import IContractRepository
from app.domain.entities.review import ReviewEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.contract import ContractStatus

class LeaveReview:

    def __init__(self, review_repo: IReviewRepository, contract_repo: IContractRepository):
        self.review_repo = review_repo
        self.contract_repo = contract_repo

    async def execute(self, data: LeaveReviewRequest, current_user: UserEntity) -> ReviewResponse:
        contract = await self.contract_repo.get_by_id(data.contract_id)
        if not contract:
            raise ValueError("Contract not found")

        if contract.status != ContractStatus.COMPLETED:
            raise ValueError("Can only review completed contracts")

        if current_user.id not in (contract.client_id, contract.freelancer_id):
            raise ValueError("You are not part of this contract")

        existing = await self.review_repo.get_by_contract_id(data.contract_id)
        if existing:
            raise ValueError("Review already exists for this contract")

        reviewee_id = (
            contract.freelancer_id
            if current_user.id == contract.client_id
            else contract.client_id
        )

        entity = ReviewEntity(
            id=uuid.uuid4(),
            contract_id=data.contract_id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee_id,
            rating=data.rating,
            comment=data.comment,
            created_at=None,
        )

        created = await self.review_repo.create(entity)
        return ReviewResponse.model_validate(created)
