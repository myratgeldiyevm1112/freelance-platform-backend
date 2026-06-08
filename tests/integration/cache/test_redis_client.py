import pytest
from unittest.mock import AsyncMock, patch
from app.infrastructure.cache import redis_client
from app.infrastructure.cache.redis_client import get_redis_client, close_redis_client

@pytest.fixture(autouse=True)
def reset_redis_singleton():
    """Фикстура для сброса глобального клиента перед каждым тестом"""
    redis_client._redis_client = None
    yield
    redis_client._redis_client = None

@pytest.mark.asyncio
@patch("redis.asyncio.from_url")
async def test_get_redis_client_initialization(mock_from_url):
    # Arrange
    mock_client = AsyncMock()
    mock_from_url.return_value = mock_client

    # Act
    client = await get_redis_client()

    # Assert
    mock_from_url.assert_called_once()
    assert client == mock_client

@pytest.mark.asyncio
@patch("redis.asyncio.from_url")
async def test_get_redis_client_singleton(mock_from_url):
    # Arrange
    mock_client = AsyncMock()
    mock_from_url.return_value = mock_client

    # Act
    client1 = await get_redis_client()
    client2 = await get_redis_client()

    # Assert
    # from_url должен вызывать только один раз, так как второй раз берется из синглтона
    mock_from_url.assert_called_once()
    assert client1 == client2

@pytest.mark.asyncio
@patch("redis.asyncio.from_url")
async def test_close_redis_client(mock_from_url):
    # Arrange
    mock_client = AsyncMock()
    mock_from_url.return_value = mock_client
    
    # Инициализируем клиент
    await get_redis_client()

    # Act
    await close_redis_client()

    # Assert
    mock_client.aclose.assert_called_once()
    assert redis_client._redis_client is None

@pytest.mark.asyncio
async def test_close_redis_client_when_none():
    # Act & Assert
    # Если клиент None, вызов не должен приводить к ошибкам
    await close_redis_client()
    assert redis_client._redis_client is None
