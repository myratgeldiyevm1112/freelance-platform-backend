import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.infrastructure.database.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5433/freelance_test_db"

@pytest_asyncio.fixture(scope="function")
async def integration_engine():
    _engine = create_async_engine(TEST_DATABASE_URL)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def integration_db_session(integration_engine):
    session_maker = async_sessionmaker(integration_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session