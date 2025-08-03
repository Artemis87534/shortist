import pytest
from httpx import AsyncClient
from src.main import app
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def prepare_db():
    from src.database import async_session, Base
    async with async_session() as session:
        await session.run_sync(Base.metadata.create_all)
        yield
        await session.run_sync(Base.metadata.drop_all)