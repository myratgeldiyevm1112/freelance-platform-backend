import uuid
import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.dependencies.auth import get_current_user

@pytest.fixture(autouse=True)
def override_auth():
    # Автоматически подменяем авторизацию для всех тестов в этом файле
    app.dependency_overrides[get_current_user] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

# 1. Тест на ошибку 404 (Уже был, оставляем)
@pytest.mark.asyncio
@patch("app.api.v1.routers.freelancers.UserRepository")
async def test_get_freelancer_profile_not_found_unit(mock_repo_class, client):
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    mock_repo_class.return_value = mock_repo
    
    random_uuid = uuid.uuid4()
    response = await client.get(f"/api/v1/freelancers/{random_uuid}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Freelancer not found"

# 2. НОВЫЙ: Тест на успешное получение профиля (Закроет строку 50)
@pytest.mark.asyncio
@patch("app.api.v1.routers.freelancers.UserRepository")
async def test_get_freelancer_profile_success_unit(mock_repo_class, client):
    mock_freelancer = AsyncMock()
    mock_freelancer.id = uuid.uuid4()
    mock_freelancer.full_name = "John Doe"
    mock_freelancer.bio = "Python Dev"
    mock_freelancer.hourly_rate = 45.0
    mock_freelancer.avatar_url = None
    mock_freelancer.portfolio_urls = []

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = mock_freelancer
    mock_repo_class.return_value = mock_repo
    
    response = await client.get(f"/api/v1/freelancers/{mock_freelancer.id}")
    
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Doe"

# 3. НОВЫЙ: Тест на успешный поиск (Закроет строки 28-29)
@pytest.mark.asyncio
@patch("app.api.v1.routers.freelancers.SearchFreelancers")
async def test_search_freelancers_success_unit(mock_use_case_class, client):
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = []
    mock_use_case_class.return_value = mock_use_case
    
    response = await client.get("/api/v1/freelancers/?skill=python")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_use_case.execute.assert_called_once()