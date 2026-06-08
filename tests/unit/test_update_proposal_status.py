import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

from app.application.use_cases.update_proposal_status import UpdateProposalStatus
from app.application.dto.proposal import ProposalResponse, AcceptProposalResponse
from app.domain.entities.job import JobEntity
from app.domain.entities.proposal import ProposalEntity
from app.domain.entities.contract import ContractEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.job import JobStatus
from app.infrastructure.database.models.proposal import ProposalStatus
from app.infrastructure.database.models.contract import ContractStatus


def make_client():
    return UserEntity(
        id=uuid.uuid4(), email="client@test.com", full_name="Client User",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )


def make_freelancer():
    return UserEntity(
        id=uuid.uuid4(), email="freelancer@test.com", full_name="Freelancer User",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )


def make_job(client_id):
    return JobEntity(
        id=uuid.uuid4(), client_id=client_id, title="Build API",
        description="Need a FastAPI dev", budget=Decimal("1000"),
        status=JobStatus.OPEN, created_at=datetime.now(),
    )


def make_proposal(job_id, freelancer_id, status=ProposalStatus.PENDING):
    return ProposalEntity(
        id=uuid.uuid4(), job_id=job_id, freelancer_id=freelancer_id,
        cover_letter="I can do this", proposed_rate=Decimal("200"),
        status=status, created_at=datetime.now(),
    )


def make_contract(job_id, proposal_id, client_id, freelancer_id):
    return ContractEntity(
        id=uuid.uuid4(), job_id=job_id, proposal_id=proposal_id,
        client_id=client_id, freelancer_id=freelancer_id,
        agreed_rate=Decimal("200"), status=ContractStatus.ACTIVE,
        created_at=datetime.now(),
    )


def make_use_case(proposal_repo, job_repo, contract_repo, user_repo, db=None):
    return UpdateProposalStatus(
        proposal_repo=proposal_repo,
        job_repo=job_repo,
        contract_repo=contract_repo,
        user_repo=user_repo,
        db=db,
    )


# --- Forbidden / auth ---

@pytest.mark.asyncio
async def test_freelancer_cannot_update_proposal_status():
    freelancer = make_freelancer()
    use_case = make_use_case(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await use_case.execute(uuid.uuid4(), ProposalStatus.ACCEPTED, freelancer)


# --- NotFound ---

@pytest.mark.asyncio
async def test_proposal_not_found():
    client = make_client()
    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = None

    use_case = make_use_case(proposal_repo, AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4(), ProposalStatus.ACCEPTED, client)


@pytest.mark.asyncio
async def test_job_not_found():
    client = make_client()
    proposal = make_proposal(uuid.uuid4(), uuid.uuid4())

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = None

    use_case = make_use_case(proposal_repo, job_repo, AsyncMock(), AsyncMock())

    with pytest.raises(NotFoundError):
        await use_case.execute(proposal.id, ProposalStatus.ACCEPTED, client)


# --- Validation ---

@pytest.mark.asyncio
async def test_proposal_not_pending_raises_validation_error():
    client = make_client()
    job = make_job(client.id)
    proposal = make_proposal(job.id, uuid.uuid4(), status=ProposalStatus.ACCEPTED)

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal

    use_case = make_use_case(proposal_repo, AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(ValidationError):
        await use_case.execute(proposal.id, ProposalStatus.REJECTED, client)


@pytest.mark.asyncio
async def test_client_does_not_own_job():
    client = make_client()
    other_client_id = uuid.uuid4()
    job = make_job(other_client_id)  # job belongs to someone else
    proposal = make_proposal(job.id, uuid.uuid4())

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = job

    use_case = make_use_case(proposal_repo, job_repo, AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await use_case.execute(proposal.id, ProposalStatus.ACCEPTED, client)


# --- Reject ---

@pytest.mark.asyncio
async def test_reject_proposal_success():
    client = make_client()
    job = make_job(client.id)
    proposal = make_proposal(job.id, uuid.uuid4())
    rejected = make_proposal(job.id, proposal.freelancer_id, status=ProposalStatus.REJECTED)
    rejected.id = proposal.id

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    proposal_repo.update_status.return_value = rejected
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = job

    use_case = make_use_case(proposal_repo, job_repo, AsyncMock(), AsyncMock())
    result = await use_case.execute(proposal.id, ProposalStatus.REJECTED, client)

    assert isinstance(result, ProposalResponse)
    proposal_repo.update_status.assert_called_once_with(proposal.id, ProposalStatus.REJECTED)


# --- Accept ---

@pytest.mark.asyncio
async def test_accept_proposal_creates_contract():
    client = make_client()
    freelancer = make_freelancer()
    job = make_job(client.id)
    proposal = make_proposal(job.id, freelancer.id)
    accepted = make_proposal(job.id, freelancer.id, status=ProposalStatus.ACCEPTED)
    accepted.id = proposal.id
    contract = make_contract(job.id, proposal.id, client.id, freelancer.id)

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    proposal_repo.update_status.return_value = accepted
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    contract_repo = AsyncMock()
    contract_repo.create.return_value = contract
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = freelancer

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        with patch("app.infrastructure.tasks.notifications.send_contract_notification") as mock_task:
            mock_task.delay = MagicMock()
            use_case = make_use_case(proposal_repo, job_repo, contract_repo, user_repo)
            result = await use_case.execute(proposal.id, ProposalStatus.ACCEPTED, client)

    assert isinstance(result, AcceptProposalResponse)
    assert result.contract_id == contract.id
    contract_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_accept_proposal_sends_notification_if_db_provided():
    client = make_client()
    freelancer = make_freelancer()
    job = make_job(client.id)
    proposal = make_proposal(job.id, freelancer.id)
    accepted = make_proposal(job.id, freelancer.id, status=ProposalStatus.ACCEPTED)
    accepted.id = proposal.id
    contract = make_contract(job.id, proposal.id, client.id, freelancer.id)

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    proposal_repo.update_status.return_value = accepted
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    contract_repo = AsyncMock()
    contract_repo.create.return_value = contract
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = freelancer

    mock_db = MagicMock()
    mock_notify = AsyncMock()

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        with patch("app.infrastructure.tasks.notifications.send_contract_notification") as mock_task:
            with patch("app.infrastructure.notifications.notification_service.NotificationService") as MockNS:
                mock_task.delay = MagicMock()
                MockNS.return_value.notify = mock_notify
                use_case = make_use_case(proposal_repo, job_repo, contract_repo, user_repo, db=mock_db)
                result = await use_case.execute(proposal.id, ProposalStatus.ACCEPTED, client)

    assert isinstance(result, AcceptProposalResponse)
    mock_notify.assert_called_once()


@pytest.mark.asyncio
async def test_accept_proposal_freelancer_not_found_still_creates_contract():
    """Если freelancer не найден — контракт всё равно создаётся, уведомления пропускаются."""
    client = make_client()
    job = make_job(client.id)
    freelancer_id = uuid.uuid4()
    proposal = make_proposal(job.id, freelancer_id)
    accepted = make_proposal(job.id, freelancer_id, status=ProposalStatus.ACCEPTED)
    accepted.id = proposal.id
    contract = make_contract(job.id, proposal.id, client.id, freelancer_id)

    proposal_repo = AsyncMock()
    proposal_repo.get_by_id.return_value = proposal
    proposal_repo.update_status.return_value = accepted
    job_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    contract_repo = AsyncMock()
    contract_repo.create.return_value = contract
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = None  # freelancer not found

    use_case = make_use_case(proposal_repo, job_repo, contract_repo, user_repo)
    result = await use_case.execute(proposal.id, ProposalStatus.ACCEPTED, client)

    assert isinstance(result, AcceptProposalResponse)
    assert result.contract_id == contract.id
