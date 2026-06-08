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
    email="contracts_tester@example.com",
    full_name="Contracts Tester",
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
@patch("app.api.v1.routers.contracts.GetContract")
async def test_get_contract_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    contract_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    
    # Добавлены все обязательные поля для схемы ContractResponse
    mock_use_case.execute.return_value = {
        "id": str(contract_id),
        "proposal_id": str(proposal_id),
        "job_id": str(uuid.uuid4()),
        "client_id": str(uuid.uuid4()),
        "freelancer_id": str(uuid.uuid4()),
        "agreed_rate": 500.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get(f"/api/v1/contracts/{contract_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == str(contract_id)
    mock_use_case.execute.assert_called_once_with(contract_id)

@pytest.mark.asyncio
@patch("app.api.v1.routers.contracts.UpdateContractStatus")
async def test_update_contract_status_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    contract_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    
    # Добавлены все обязательные поля для схемы ContractResponse
    mock_use_case.execute.return_value = {
        "id": str(contract_id),
        "proposal_id": str(proposal_id),
        "job_id": str(uuid.uuid4()),
        "client_id": str(uuid.uuid4()),
        "freelancer_id": str(uuid.uuid4()),
        "agreed_rate": 500.0,
        "status": "completed",
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    mock_use_case.execute.assert_called_once_with(
        contract_id=contract_id,
        new_status="completed",
        current_user=mock_user
    )