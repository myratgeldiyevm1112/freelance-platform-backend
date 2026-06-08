import uuid
import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.api.dependencies.cache import get_redis
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole
from datetime import datetime

# Фиктивный пользователь-клиент для прохождения Depends(get_current_user)
mock_client_user = UserEntity(
    id=uuid.uuid4(),
    email="client_tester@example.com",
    full_name="Client Tester",
    role=UserRole.CLIENT,
    is_active=True,
    created_at=datetime.now()
)

@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: mock_client_user
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_redis] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.api.v1.routers.jobs.CreateJob")
async def test_create_job_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = {
        "id": str(uuid.uuid4()),
        "client_id": str(mock_client_user.id),
        "title": "Test Job Title",
        "description": "Test description",
        "budget": 500.0,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job Title", "description": "Test description", "budget": 500}
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test Job Title"
    mock_use_case_class.return_value.execute.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.v1.routers.jobs.GetJobs")
async def test_get_jobs_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "client_id": str(mock_client_user.id),
                "title": "Job 1",
                "description": "Desc 1",
                "budget": 300.0,
                "status": "open",
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "pages": 1
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get("/api/v1/jobs/?page=1&page_size=20")

    # Assert
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Job 1"
    mock_use_case_class.return_value.execute.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.v1.routers.jobs.GetJobs")
async def test_get_single_job_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    job_id = uuid.uuid4()
    
    # Настраиваем execute_one так, чтобы при await он сразу отдавал нужный словарь
    mock_use_case.execute_one.return_value = {
        "id": str(job_id),
        "client_id": str(mock_client_user.id),
        "title": "Single Job",
        "description": "Desc",
        "budget": 1000.0,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get(f"/api/v1/jobs/{job_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == str(job_id)
    assert response.json()["title"] == "Single Job"
    mock_use_case.execute_one.assert_called_once_with(job_id)