import uuid
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole

# Фейковый пользователь
mock_user = UserEntity(
    id=uuid.uuid4(),
    email="dispute_admin@example.com",
    full_name="Dispute Admin",
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
@patch("app.api.v1.routers.disputes.OpenDispute")
async def test_open_dispute_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    dispute_id = uuid.uuid4()
    contract_id = uuid.uuid4()
    
    mock_use_case.execute.return_value = {
        "id": str(dispute_id),
        "contract_id": str(contract_id),
        "opened_by": str(mock_user.id),
        "reason": "Wrong delivery format",
        "status": "open",  # Исправлено на 'open'
        "resolution": None,
        "resolution_note": None,
        "resolved_by": None,  # Добавлено обязательное поле
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.post(
        "/api/v1/disputes/",
        json={
            "contract_id": str(contract_id),
            "reason": "Wrong delivery format"
        }
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == str(dispute_id)
    mock_use_case.execute.assert_called_once_with(
        contract_id=contract_id,
        reason="Wrong delivery format",
        current_user=mock_user
    )

@pytest.mark.asyncio
@patch("app.api.v1.routers.disputes.GetDisputes")
async def test_get_all_disputes_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    dispute_id = uuid.uuid4()
    contract_id = uuid.uuid4()
    
    mock_use_case.execute.return_value = [
        {
            "id": str(dispute_id),
            "contract_id": str(contract_id),
            "opened_by": str(uuid.uuid4()),
            "reason": "Delay",
            "status": "open",  # Исправлено на 'open'
            "resolution": None,
            "resolution_note": None,
            "resolved_by": None,  # Добавлено обязательное поле
            "created_at": datetime.now().isoformat()
        }
    ]
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get("/api/v1/disputes/admin?limit=10&offset=0")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(dispute_id)
    mock_use_case.execute.assert_called_once_with(limit=10, offset=0)

@pytest.mark.asyncio
@patch("app.api.v1.routers.disputes.ResolveDispute")
async def test_resolve_dispute_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    dispute_id = uuid.uuid4()
    contract_id = uuid.uuid4()
    
    mock_use_case.execute.return_value = {
        "id": str(dispute_id),
        "contract_id": str(contract_id),
        "opened_by": str(uuid.uuid4()),
        "reason": "Delay",
        "status": "resolved_refund",
        "resolution": "resolved_refund",
        "resolution_note": "Work was not done.",
        "resolved_by": str(mock_user.id),
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.patch(
        f"/api/v1/disputes/{dispute_id}/resolve",
        json={
            "resolution": "refund",  # Изменено с 'resolved_refund' на 'refund'
            "resolution_note": "Work was not done."
        }
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "resolved_refund"
    mock_use_case.execute.assert_called_once_with(
        dispute_id=dispute_id,
        resolution="refund",  # Проверяем, что в юзкейс ушло исходное значение
        resolution_note="Work was not done.",
        current_user=mock_user
    )