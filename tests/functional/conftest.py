import pytest_asyncio
import pytest
from httpx import AsyncClient
from src.main import app
from src.database import Base, async_engine

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)