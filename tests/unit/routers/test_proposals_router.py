import uuid
import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole
from datetime import datetime

# Фейковый пользователь
mock_user = UserEntity(
    id=uuid.uuid4(),
    email="proposals_tester@example.com",
    full_name="Proposals Tester",
    role=UserRole.CLIENT,
    is_active=True,
    created_at=datetime.now()
)

@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.api.v1.routers.proposals.SubmitProposal")
async def test_submit_proposal_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    job_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    
    # Исправлено bid_amount -> proposed_rate под ProposalResponse
    mock_use_case.execute.return_value = {
        "id": str(proposal_id),
        "job_id": str(job_id),
        "freelancer_id": str(mock_user.id),
        "cover_letter": "I can build this app!",
        "proposed_rate": 450.0,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    # В теле запроса передаем proposed_rate
    response = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can build this app!", "proposed_rate": 450.0}
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == str(proposal_id)
    mock_use_case.execute.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.v1.routers.proposals.GetProposals")
async def test_get_proposals_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    job_id = uuid.uuid4()
    
    mock_use_case.execute_by_job.return_value = [
        {
            "id": str(uuid.uuid4()),
            "job_id": str(job_id),
            "freelancer_id": str(uuid.uuid4()),
            "cover_letter": "Some application",
            "proposed_rate": 300.0,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    ]
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get(f"/api/v1/proposals/jobs/{job_id}/proposals")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_use_case.execute_by_job.assert_called_once_with(job_id, mock_user)

@pytest.mark.asyncio
@patch("app.api.v1.routers.proposals.UpdateProposalStatus")
async def test_update_proposal_status_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    proposal_id = uuid.uuid4()
    contract_id = uuid.uuid4()
    job_id = uuid.uuid4()
    freelancer_id = uuid.uuid4()
    
    # Формируем структуру под AcceptProposalResponse схему
    mock_use_case.execute.return_value = {
        "contract_id": str(contract_id),
        "proposal": {
            "id": str(proposal_id),
            "job_id": str(job_id),
            "freelancer_id": str(freelancer_id),
            "cover_letter": "Some application",
            "proposed_rate": 300.0,
            "status": "accepted",
            "created_at": datetime.now().isoformat()
        }
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["contract_id"] == str(contract_id)
    assert response.json()["proposal"]["status"] == "accepted"
    mock_use_case.execute.assert_called_once_with(proposal_id, "accepted", mock_user)