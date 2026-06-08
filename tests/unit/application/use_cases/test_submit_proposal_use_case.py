import uuid
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from decimal import Decimal
from app.application.use_cases.submit_proposal import SubmitProposal
from app.application.dto.proposal import SubmitProposalRequest
from app.domain.entities.job import JobEntity
from app.domain.entities.proposal import ProposalEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ForbiddenError, NotFoundError, ValidationError, ConflictError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.job import JobStatus
from app.infrastructure.database.models.proposal import ProposalStatus


def make_freelancer():
    return UserEntity(
        id=uuid.uuid4(), email="f@test.com", full_name="Freelancer",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )

def make_client():
    return UserEntity(
        id=uuid.uuid4(), email="c@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )

def make_job(status=JobStatus.OPEN):
    return JobEntity(
        id=uuid.uuid4(), client_id=uuid.uuid4(), title="Job",
        description="Desc", budget=Decimal("500"), status=status,
        created_at=datetime.now(),
    )

def make_proposal(job_id, freelancer_id):
    return ProposalEntity(
        id=uuid.uuid4(), job_id=job_id, freelancer_id=freelancer_id,
        cover_letter="I can do this job well", proposed_rate=Decimal("100"),
        status=ProposalStatus.PENDING, created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_submit_proposal_success():
    freelancer = make_freelancer()
    job = make_job()
    proposal = make_proposal(job.id, freelancer.id)

    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    proposal_repo.get_by_freelancer_and_job.return_value = None
    proposal_repo.create.return_value = proposal
    user_repo.get_by_id.return_value = make_client()

    use_case = SubmitProposal(proposal_repo, job_repo, user_repo)
    result = await use_case.execute(
        job.id,
        SubmitProposalRequest(cover_letter="I can do this job well", proposed_rate=100),
        freelancer
    )

    assert result.job_id == job.id
    proposal_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_submit_proposal_client_forbidden():
    client = make_client()
    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()

    use_case = SubmitProposal(proposal_repo, job_repo, user_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(
            uuid.uuid4(),
            SubmitProposalRequest(cover_letter="I can do this job well", proposed_rate=100),
            client
        )


@pytest.mark.asyncio
async def test_submit_proposal_job_not_found():
    freelancer = make_freelancer()
    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    job_repo.get_by_id.return_value = None

    use_case = SubmitProposal(proposal_repo, job_repo, user_repo)

    with pytest.raises(NotFoundError):
        await use_case.execute(
            uuid.uuid4(),
            SubmitProposalRequest(cover_letter="I can do this job well", proposed_rate=100),
            freelancer
        )


@pytest.mark.asyncio
async def test_submit_proposal_job_not_open():
    freelancer = make_freelancer()
    job = make_job(status=JobStatus.CLOSED)
    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    job_repo.get_by_id.return_value = job

    use_case = SubmitProposal(proposal_repo, job_repo, user_repo)

    with pytest.raises(ValidationError):
        await use_case.execute(
            job.id,
            SubmitProposalRequest(cover_letter="I can do this job well", proposed_rate=100),
            freelancer
        )


@pytest.mark.asyncio
async def test_submit_proposal_duplicate():
    freelancer = make_freelancer()
    job = make_job()
    existing = make_proposal(job.id, freelancer.id)

    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    proposal_repo.get_by_freelancer_and_job.return_value = existing

    use_case = SubmitProposal(proposal_repo, job_repo, user_repo)

    with pytest.raises(ConflictError):
        await use_case.execute(
            job.id,
            SubmitProposalRequest(cover_letter="I can do this job well", proposed_rate=100),
            freelancer
        )