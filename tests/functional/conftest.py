import uuid
import pytest_asyncio
from httpx import AsyncClient
from src.main import app
from src.database import Base, async_engine
from src.auth.schemas import UserRead


class MockUserManager:
    async def create(self, user_create, safe=True, request=None):
        return UserRead(
            id=uuid.uuid4(),
            email=user_create.email,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(monkeypatch):
    try:
        from src.auth import routes
        monkeypatch.setattr(routes, "get_user_manager", lambda: MockUserManager())
    except ImportError:
        pass

    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def test_client(client):
    yield client