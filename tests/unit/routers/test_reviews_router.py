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

# Фейковый авторизованный пользователь
mock_user = UserEntity(
    id=uuid.uuid4(),
    email="reviewer@example.com",
    full_name="Reviewer Tester",
    role=UserRole.CLIENT,
    is_active=True,
    created_at=datetime.now()
)

@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_redis] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.api.v1.routers.reviews.RatingCache")
@patch("app.api.v1.routers.reviews.LeaveReview")
async def test_leave_review_success(mock_use_case_class, mock_cache_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_cache = AsyncMock()
    
    review_id = uuid.uuid4()
    contract_id = uuid.uuid4()
    reviewee_id = uuid.uuid4()
    
    # Имитируем успешный результат выполнения юзкейса
    mock_result = AsyncMock()
    mock_result.reviewee_id = reviewee_id
    # Для валидации Pydantic-схемы ReviewResponse возвращаем словарь/объект с нужными полями
    mock_use_case.execute.return_value = {
        "id": str(review_id),
        "contract_id": str(contract_id),
        "reviewer_id": str(mock_user.id),
        "reviewee_id": str(reviewee_id),
        "rating": 5,
        "comment": "Excellent work!",
        "created_at": datetime.now().isoformat()
    }
    # Подменяем reviewee_id на объекте, чтобы сработал .reviewee_id в роутере
    class DictLikeMock(dict):
        def __getattr__(self, name):
            return self[name]
            
    mock_use_case.execute.return_value = DictLikeMock(mock_use_case.execute.return_value)
    
    mock_use_case_class.return_value = mock_use_case
    mock_cache_class.return_value = mock_cache

    # Act
    response = await client.post(
        "/api/v1/reviews/",
        json={
            "contract_id": str(contract_id),
            "rating": 5,
            "comment": "Excellent work!"
        }
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == str(review_id)
    mock_use_case.execute.assert_called_once()
    mock_cache.invalidate.assert_called_once_with(str(reviewee_id))


@pytest.mark.asyncio
@patch("app.api.v1.routers.reviews.ReviewRepository")
async def test_get_user_reviews_success(mock_repo_class, override_dependencies, client):
    # Arrange
    mock_repo = AsyncMock()
    user_id = uuid.uuid4()
    
    # Имитируем список отзывов из БД
    mock_repo.get_by_reviewee_id.return_value = [
        {
            "id": uuid.uuid4(),
            "contract_id": uuid.uuid4(),
            "reviewer_id": uuid.uuid4(),
            "reviewee_id": user_id,
            "rating": 4,
            "comment": "Good job",
            "created_at": datetime.now()
        }
    ]
    mock_repo_class.return_value = mock_repo

    # Act
    response = await client.get(f"/api/v1/reviews/user/{user_id}")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["rating"] == 4
    mock_repo.get_by_reviewee_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
@patch("app.api.v1.routers.reviews.RatingCache")
async def test_get_user_rating_from_cache(mock_cache_class, override_dependencies, client):
    # Arrange
    mock_cache = AsyncMock()
    user_id = uuid.uuid4()
    
    # Сценарий 1: Данные есть в кэше Redis
    mock_cache.get.return_value = {"average_rating": 4.8, "review_count": 10}
    mock_cache_class.return_value = mock_cache

    # Act
    response = await client.get(f"/api/v1/reviews/user/{user_id}/rating")

    # Assert
    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.8
    mock_cache.get.assert_called_once_with(user_id)


@pytest.mark.asyncio
@patch("app.api.v1.routers.reviews.ReviewRepository")
@patch("app.api.v1.routers.reviews.RatingCache")
async def test_get_user_rating_from_db(mock_cache_class, mock_repo_class, override_dependencies, client):
    # Arrange
    mock_cache = AsyncMock()
    mock_repo = AsyncMock()
    user_id = uuid.uuid4()
    
    # Сценарий 2: В кэше пусто, идем в репозиторий БД
    mock_cache.get.return_value = None
    mock_repo.get_average_rating.return_value = {"average_rating": 4.5, "review_count": 5}
    
    mock_cache_class.return_value = mock_cache
    mock_repo_class.return_value = mock_repo

    # Act
    response = await client.get(f"/api/v1/reviews/user/{user_id}/rating")

    # Assert
    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.5
    mock_cache.get.assert_called_once_with(user_id)
    mock_repo.get_average_rating.assert_called_once_with(user_id)
    mock_cache.set.assert_called_once_with(user_id, {"average_rating": 4.5, "review_count": 5})
