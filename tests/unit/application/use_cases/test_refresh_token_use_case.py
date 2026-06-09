import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.application.use_cases.refresh_token import RefreshToken
from app.domain.exceptions import ValidationError, NotFoundError, ForbiddenError, UnauthorizedError
from app.application.dto.auth import TokenResponse

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def mock_token_store():
    return AsyncMock()

@pytest.fixture
def refresh_token_use_case(mock_user_repo, mock_token_store):
    return RefreshToken(user_repo=mock_user_repo, token_store=mock_token_store)

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
@patch("app.application.use_cases.refresh_token.create_refresh_token")
@patch("app.application.use_cases.refresh_token.create_access_token")
async def test_refresh_token_success(
    mock_create_access, mock_create_refresh, mock_decode, 
    refresh_token_use_case, mock_user_repo, mock_token_store
):
    # Arrange
    mock_decode.return_value = {"type": "refresh", "sub": "user_123"}
    mock_token_store.get.return_value = "old_refresh_token"
    
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.role = "freelancer"
    mock_user.is_active = True
    mock_user_repo.get_by_id.return_value = mock_user

    mock_create_refresh.return_value = "new_refresh_token"
    mock_create_access.return_value = "new_access_token"

    # Act
    result = await refresh_token_use_case.execute("old_refresh_token")

    # Assert
    assert isinstance(result, TokenResponse)
    assert result.access_token == "new_access_token"
    assert result.refresh_token == "new_refresh_token"
    mock_token_store.save.assert_called_once_with("user_123", "new_refresh_token")

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
async def test_refresh_token_invalid_token(mock_decode, refresh_token_use_case):
    # Arrange
    mock_decode.side_effect = ValueError("Invalid signature")

    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid refresh token"):
        await refresh_token_use_case.execute("bad_token")

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
async def test_refresh_token_invalid_type(mock_decode, refresh_token_use_case):
    # Arrange
    mock_decode.return_value = {"type": "access", "sub": "user_123"}

    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid token type"):
        await refresh_token_use_case.execute("access_token_instead_of_refresh")

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
async def test_refresh_token_expired_or_missing_in_store(mock_decode, refresh_token_use_case, mock_token_store):
    # Arrange
    mock_decode.return_value = {"type": "refresh", "sub": "user_123"}
    mock_token_store.get.return_value = None  # Нет в кэше

    # Act & Assert
    with pytest.raises(UnauthorizedError):
        await refresh_token_use_case.execute("some_token")

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
async def test_refresh_token_user_not_found(mock_decode, refresh_token_use_case, mock_user_repo, mock_token_store):
    # Arrange
    mock_decode.return_value = {"type": "refresh", "sub": "user_123"}
    mock_token_store.get.return_value = "valid_token"
    mock_user_repo.get_by_id.return_value = None  # Юзер удален

    # Act & Assert
    with pytest.raises(NotFoundError, match="User not found"):
        await refresh_token_use_case.execute("valid_token")

@pytest.mark.asyncio
@patch("app.application.use_cases.refresh_token.decode_token")
async def test_refresh_token_user_inactive(mock_decode, refresh_token_use_case, mock_user_repo, mock_token_store):
    # Arrange
    mock_decode.return_value = {"type": "refresh", "sub": "user_123"}
    mock_token_store.get.return_value = "valid_token"
    
    mock_user = MagicMock()
    mock_user.is_active = False  # Юзер забанен
    mock_user_repo.get_by_id.return_value = mock_user

    # Act & Assert
    with pytest.raises(ForbiddenError, match="User is inactive"):
        await refresh_token_use_case.execute("valid_token")
