import uuid
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from decimal import Decimal
from app.application.use_cases.leave_review import LeaveReview
from app.application.dto.review import LeaveReviewRequest
from app.domain.entities.contract import ContractEntity
from app.domain.entities.review import ReviewEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ValidationError, ForbiddenError, ConflictError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.contract import ContractStatus


def make_client():
    return UserEntity(
        id=uuid.uuid4(), email="c@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )

def make_contract(client_id, freelancer_id, status=ContractStatus.COMPLETED):
    return ContractEntity(
        id=uuid.uuid4(), job_id=uuid.uuid4(), proposal_id=uuid.uuid4(),
        client_id=client_id, freelancer_id=freelancer_id,
        agreed_rate=Decimal("500"), status=status, created_at=datetime.now(),
    )

def make_review(contract_id, reviewer_id, reviewee_id):
    return ReviewEntity(
        id=uuid.uuid4(), contract_id=contract_id,
        reviewer_id=reviewer_id, reviewee_id=reviewee_id,
        rating=5, comment="Great!", created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_leave_review_success():
    client = make_client()
    freelancer_id = uuid.uuid4()
    contract = make_contract(client.id, freelancer_id)
    review = make_review(contract.id, client.id, freelancer_id)

    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    contract_repo.get_by_id.return_value = contract
    review_repo.get_by_contract_id.return_value = None
    review_repo.create.return_value = review

    use_case = LeaveReview(review_repo, contract_repo)
    result = await use_case.execute(
        LeaveReviewRequest(contract_id=contract.id, rating=5, comment="Great!"),
        client
    )

    assert result.rating == 5
    review_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_leave_review_contract_not_found():
    client = make_client()
    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    contract_repo.get_by_id.return_value = None

    use_case = LeaveReview(review_repo, contract_repo)

    with pytest.raises(NotFoundError):
        await use_case.execute(
            LeaveReviewRequest(contract_id=uuid.uuid4(), rating=5),
            client
        )


@pytest.mark.asyncio
async def test_leave_review_contract_not_completed():
    client = make_client()
    contract = make_contract(client.id, uuid.uuid4(), status=ContractStatus.ACTIVE)

    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    contract_repo.get_by_id.return_value = contract

    use_case = LeaveReview(review_repo, contract_repo)

    with pytest.raises(ValidationError):
        await use_case.execute(
            LeaveReviewRequest(contract_id=contract.id, rating=5),
            client
        )


@pytest.mark.asyncio
async def test_leave_review_not_participant():
    other_user = make_client()
    contract = make_contract(uuid.uuid4(), uuid.uuid4())

    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    contract_repo.get_by_id.return_value = contract

    use_case = LeaveReview(review_repo, contract_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(
            LeaveReviewRequest(contract_id=contract.id, rating=5),
            other_user
        )


@pytest.mark.asyncio
async def test_leave_review_duplicate():
    client = make_client()
    freelancer_id = uuid.uuid4()
    contract = make_contract(client.id, freelancer_id)
    existing = make_review(contract.id, client.id, freelancer_id)

    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    contract_repo.get_by_id.return_value = contract
    review_repo.get_by_contract_id.return_value = existing

    use_case = LeaveReview(review_repo, contract_repo)

    with pytest.raises(ConflictError):
        await use_case.execute(
            LeaveReviewRequest(contract_id=contract.id, rating=5),
            client
        )