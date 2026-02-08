import os
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.db_hepler import db_helper
from app.main import app

TEST_DB_URL = os.getenv(
    "APP_CONFIG__DB__URL",
    "postgresql+asyncpg://user:password@db_test:5432/logistic_test"
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a function-scoped asynchronous database session for testing.

    This fixture creates a dedicated engine and session for each test function.
    After the test runs, it automatically rolls back the transaction to ensure
    a clean state for the next test.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session connected to the test database.
    """
    engine = create_async_engine(TEST_DB_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an asynchronous HTTP client for testing FastAPI endpoints.

    This fixture overrides the application's database dependency to use the
    `db_session` test fixture, ensuring tests run against the isolated test DB transaction.

    Args:
        db_session: The asynchronous database session fixture.

    Yields:
        AsyncClient: An asynchronous HTTP client instance configured for the FastAPI app.
    """
    async def override_session_getter() -> AsyncGenerator[AsyncSession, None]:
        """
        Overrides the default database session getter for testing.

        This internal async function is used within a pytest fixture to inject
        a predefined test `db_session` into FastAPI's dependency injection system,
        isolating tests from the main application database connection.

        Yields:
            AsyncSession: The asynchronous database session for the test scope.
        """
        yield db_session

    app.dependency_overrides[db_helper.session_getter] = override_session_getter

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
