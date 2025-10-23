import os
import logging

# Set up logger ------------------
logger = logging.getLogger("Test")
logger.setLevel(logging.DEBUG)

# set ENV for use settings as test important for run pytest
os.environ["ENV"] = "test"
logger.info(f"SET ENV : test")

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.setup import Base
from app.main import app
from app.db.session import get_session_pool


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def create_engine():
    logger.info("Setting up test engine")

    async def init_models(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_models(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    asyncio.get_event_loop().run_until_complete(init_models(engine))
    yield engine
    asyncio.get_event_loop().run_until_complete(drop_models(engine))
    asyncio.get_event_loop().run_until_complete(engine.dispose())
    logger.info("✅ Test engine disposed.")


@pytest.fixture(scope="session")
def create_session_pool(create_engine):
    """This fixture create a virtual session for test"""
    logger.info("Setting up session pool")

    async_session_pool = async_sessionmaker(bind=create_engine, expire_on_commit=False)
    async def _get_session():
        async with async_session_pool() as session:
            yield session

    return _get_session


@pytest.fixture(scope="session")
def pre_load(create_session_pool):
    logger.info("Setting up override session pool")
    app.dependency_overrides[get_session_pool] = create_session_pool


@pytest.fixture(scope="session")
def client(pre_load):
    logger.info("Setting up test client")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
