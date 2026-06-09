import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

from app.application.use_cases.admin_users import GetAllUsers, BanUser, UnbanUser
from app.application.use_cases.admin_stats import GetPlatformStats
from app.application.use_cases.admin_jobs import GetAllJobs, DeleteJob
from app.domain.entities.user import UserEntity
from app.domain.entities.job import JobEntity
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.job import JobStatus


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_user_entity(is_active=True):
    return UserEntity(
        id=uuid.uuid4(), email="user@test.com", full_name="Test User",
        role=UserRole.FREELANCER, is_active=is_active, created_at=datetime.now(),
    )


def make_job_entity():
    return JobEntity(
        id=uuid.uuid4(), client_id=uuid.uuid4(), title="Test Job",
        description="Description", budget=Decimal("500"),
        status=JobStatus.OPEN, created_at=datetime.now(),
    )


def make_db_mock():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.scalar = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


# ─── GetAllUsers ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_users_returns_list():
    user = make_user_entity()
    db = make_db_mock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["raw_user"]
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo._to_entity.return_value = user
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.user_repository.UserRepository", mock_repo_cls):
        use_case = GetAllUsers(db)
        result = await use_case.execute(limit=10, offset=0)

    assert len(result) == 1
    assert result[0].email == user.email


@pytest.mark.asyncio
async def test_get_all_users_empty():
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.user_repository.UserRepository", mock_repo_cls):
        use_case = GetAllUsers(db)
        result = await use_case.execute()

    assert result == []


@pytest.mark.asyncio
async def test_get_all_users_multiple():
    users = [make_user_entity(), make_user_entity()]
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["u1", "u2"]
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo._to_entity.side_effect = users
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.user_repository.UserRepository", mock_repo_cls):
        use_case = GetAllUsers(db)
        result = await use_case.execute(limit=20, offset=0)

    assert len(result) == 2


# ─── BanUser ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ban_user_success():
    user_entity = make_user_entity(is_active=False)
    db = make_db_mock()

    mock_user = MagicMock()
    mock_user.is_active = True
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo._to_entity.return_value = user_entity
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.user_repository.UserRepository", mock_repo_cls):
        use_case = BanUser(db)
        result = await use_case.execute(uuid.uuid4())

    assert mock_user.is_active is False
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_ban_user_not_found():
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    use_case = BanUser(db)

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4())


# ─── UnbanUser ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unban_user_success():
    user_entity = make_user_entity(is_active=True)
    db = make_db_mock()

    mock_user = MagicMock()
    mock_user.is_active = False
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo._to_entity.return_value = user_entity
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.user_repository.UserRepository", mock_repo_cls):
        use_case = UnbanUser(db)
        result = await use_case.execute(uuid.uuid4())

    assert mock_user.is_active is True
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_unban_user_not_found():
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    use_case = UnbanUser(db)

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4())


# ─── GetPlatformStats ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_stats_returns_dict():
    db = make_db_mock()
    db.scalar.side_effect = [10, 20, 15, 5, 8, Decimal("1500.00"), 3]

    use_case = GetPlatformStats(db)
    result = await use_case.execute()

    assert result["total_users"] == 10
    assert result["total_jobs"] == 20
    assert result["total_contracts"] == 15
    assert result["active_contracts"] == 5
    assert result["completed_contracts"] == 8
    assert result["total_platform_revenue"] == 1500.0
    assert result["open_disputes"] == 3


@pytest.mark.asyncio
async def test_get_stats_handles_none_values():
    db = make_db_mock()
    db.scalar.side_effect = [0, 0, 0, 0, 0, None, 0]

    use_case = GetPlatformStats(db)
    result = await use_case.execute()

    assert result["total_platform_revenue"] == 0.0
    assert result["total_users"] == 0


@pytest.mark.asyncio
async def test_get_stats_calls_db_seven_times():
    db = make_db_mock()
    db.scalar.side_effect = [1, 2, 3, 4, 5, Decimal("100"), 6]

    use_case = GetPlatformStats(db)
    await use_case.execute()

    assert db.scalar.call_count == 7


# ─── GetAllJobs ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_jobs_returns_list():
    job = make_job_entity()
    db = make_db_mock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["raw_job"]
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo._to_entity.return_value = job
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.job_repository.JobRepository", mock_repo_cls):
        use_case = GetAllJobs(db)
        result = await use_case.execute(limit=10, offset=0)

    assert len(result) == 1
    assert result[0].title == "Test Job"


@pytest.mark.asyncio
async def test_get_all_jobs_empty():
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    mock_repo = MagicMock()
    mock_repo_cls = MagicMock(return_value=mock_repo)

    with patch("app.infrastructure.repositories.job_repository.JobRepository", mock_repo_cls):
        use_case = GetAllJobs(db)
        result = await use_case.execute()

    assert result == []


# ─── DeleteJob ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_job_success():
    db = make_db_mock()
    mock_job = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_job
    db.execute.return_value = mock_result

    use_case = DeleteJob(db)
    await use_case.execute(uuid.uuid4())

    db.delete.assert_called_once_with(mock_job)
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_job_not_found():
    db = make_db_mock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    use_case = DeleteJob(db)

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4())