import uuid
import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.create_job import CreateJob
from app.application.dto.job import CreateJobRequest
from app.domain.entities.job import JobEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ForbiddenError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.job import JobStatus
from datetime import datetime
from decimal import Decimal


def make_client():
    return UserEntity(
        id=uuid.uuid4(),
        email="client@test.com",
        full_name="Client",
        role=UserRole.CLIENT,
        is_active=True,
        created_at=datetime.now(),
    )

def make_freelancer():
    return UserEntity(
        id=uuid.uuid4(),
        email="freelancer@test.com",
        full_name="Freelancer",
        role=UserRole.FREELANCER,
        is_active=True,
        created_at=datetime.now(),
    )

def make_job_entity(client_id):
    return JobEntity(
        id=uuid.uuid4(),
        client_id=client_id,
        title="Test Job",
        description="Test description",
        budget=Decimal("500.00"),
        status=JobStatus.OPEN,
        created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_create_job_success():
    client = make_client()
    mock_repo = AsyncMock()
    mock_repo.create.return_value = make_job_entity(client.id)

    use_case = CreateJob(mock_repo)
    result = await use_case.execute(
        CreateJobRequest(title="Test Job", description="Test description", budget=500),
        client
    )

    assert result.title == "Test Job"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_job_forbidden_for_freelancer():
    freelancer = make_freelancer()
    mock_repo = AsyncMock()

    use_case = CreateJob(mock_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(
            CreateJobRequest(title="Test Job", description="Test description", budget=500),
            freelancer
        )

    mock_repo.create.assert_not_called()
