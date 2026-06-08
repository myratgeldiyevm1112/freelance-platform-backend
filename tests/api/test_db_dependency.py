import pytest
from unittest.mock import AsyncMock, patch

from app.api.dependencies.db import get_db


@pytest.mark.asyncio
async def test_get_db_commit():
    mock_session = AsyncMock()

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session
    mock_cm.__aexit__.return_value = None

    with patch("app.api.dependencies.db.async_session_maker", return_value=mock_cm):

        gen = get_db()
        session = await gen.__anext__()

        assert session == mock_session

        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

        mock_session.commit.assert_awaited_once()
        mock_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_get_db_rollback():
    mock_session = AsyncMock()

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session

    # 💥 важно: заставляем session.commit упасть
    mock_session.commit.side_effect = Exception("DB error")

    with patch("app.api.dependencies.db.async_session_maker", return_value=mock_cm):

        gen = get_db()
        await gen.__anext__()

        try:
            await gen.__anext__()
        except Exception:
            pass

        mock_session.rollback.assert_awaited_once()