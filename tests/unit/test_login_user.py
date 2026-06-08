import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.use_cases.login_user import LoginUser
from app.application.dto.auth import LoginRequest, TokenResponse
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ValidationError, ForbiddenError, UnauthorizedError
from app.infrastructure.database.models.user import UserRole


def make_user(is_active=True):
    return UserEntity(
        id=uuid.uuid4(), email="user@test.com", full_name="Test User",
        role=UserRole.FREELANCER, is_active=is_active, created_at=datetime.now(),
    )


def make_use_case(user_repo, token_store):
    return LoginUser(user_repo=user_repo, token_store=token_store)


# --- Success ---

@pytest.mark.asyncio
async def test_login_success():
    user = make_user()
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = user
    user_repo.get_hashed_password.return_value = "$2b$12$validhashedpassword"
    token_store = AsyncMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.application.use_cases.login_user.verify_password", return_value=True
    ):
        with __import__("unittest.mock", fromlist=["patch"]).patch(
            "app.application.use_cases.login_user.create_access_token", return_value="access_token"
        ):
            with __import__("unittest.mock", fromlist=["patch"]).patch(
                "app.application.use_cases.login_user.create_refresh_token", return_value="refresh_token"
            ):
                use_case = make_use_case(user_repo, token_store)
                result = await use_case.execute(LoginRequest(email="user@test.com", password="password123"))

    assert isinstance(result, TokenResponse)
    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"
    token_store.save.assert_called_once_with(str(user.id), "refresh_token")


# --- User not found ---

@pytest.mark.asyncio
async def test_login_user_not_found():
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = None
    token_store = AsyncMock()

    use_case = make_use_case(user_repo, token_store)

    with pytest.raises(ValidationError):
        await use_case.execute(LoginRequest(email="noone@test.com", password="pass"))


# --- Inactive user ---

@pytest.mark.asyncio
async def test_login_inactive_user():
    user = make_user(is_active=False)
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = user
    token_store = AsyncMock()

    use_case = make_use_case(user_repo, token_store)

    with pytest.raises(ForbiddenError):
        await use_case.execute(LoginRequest(email="user@test.com", password="pass"))


# --- Wrong password ---

@pytest.mark.asyncio
async def test_login_wrong_password():
    user = make_user()
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = user
    user_repo.get_hashed_password.return_value = "$2b$12$validhashedpassword"
    token_store = AsyncMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.application.use_cases.login_user.verify_password", return_value=False
    ):
        use_case = make_use_case(user_repo, token_store)

        with pytest.raises(UnauthorizedError):
            await use_case.execute(LoginRequest(email="user@test.com", password="wrongpass"))


# --- Token store is called ---

@pytest.mark.asyncio
async def test_login_saves_refresh_token():
    user = make_user()
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = user
    user_repo.get_hashed_password.return_value = "$2b$12$validhashedpassword"
    token_store = AsyncMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.application.use_cases.login_user.verify_password", return_value=True
    ):
        with __import__("unittest.mock", fromlist=["patch"]).patch(
            "app.application.use_cases.login_user.create_refresh_token", return_value="rt_xyz"
        ):
            with __import__("unittest.mock", fromlist=["patch"]).patch(
                "app.application.use_cases.login_user.create_access_token", return_value="at_xyz"
            ):
                use_case = make_use_case(user_repo, token_store)
                await use_case.execute(LoginRequest(email="user@test.com", password="pass"))

    token_store.save.assert_called_once_with(str(user.id), "rt_xyz")


# --- Client role can also login ---

@pytest.mark.asyncio
async def test_login_client_role_success():
    user = UserEntity(
        id=uuid.uuid4(), email="client@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = user
    user_repo.get_hashed_password.return_value = "$2b$12$hash"
    token_store = AsyncMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.application.use_cases.login_user.verify_password", return_value=True
    ):
        with __import__("unittest.mock", fromlist=["patch"]).patch(
            "app.application.use_cases.login_user.create_access_token", return_value="at"
        ):
            with __import__("unittest.mock", fromlist=["patch"]).patch(
                "app.application.use_cases.login_user.create_refresh_token", return_value="rt"
            ):
                use_case = make_use_case(user_repo, token_store)
                result = await use_case.execute(LoginRequest(email="client@test.com", password="pass"))

    assert result.access_token == "at"
