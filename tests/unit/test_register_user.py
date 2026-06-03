import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.register_user import RegisterUser
from app.application.dto.auth import RegisterRequest
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ConflictError
from app.infrastructure.database.models.user import UserRole
from datetime import datetime


def make_user_entity():
    return UserEntity(
        id=uuid.uuid4(),
        email="test@test.com",
        full_name="Test User",
        role=UserRole.CLIENT,
        is_active=True,
        created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_register_success():
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = make_user_entity()

    use_case = RegisterUser(mock_repo)
    result = await use_case.execute(RegisterRequest(
        email="test@test.com",
        password="password123",
        full_name="Test User",
        role="client"
    ))

    assert result.email == "test@test.com"
    mock_repo.get_by_email.assert_called_once_with("test@test.com")
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email():
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = make_user_entity()

    use_case = RegisterUser(mock_repo)

    with pytest.raises(ConflictError):
        await use_case.execute(RegisterRequest(
            email="test@test.com",
            password="password123",
            full_name="Test User",
            role="client"
        ))

    mock_repo.create.assert_not_called()
