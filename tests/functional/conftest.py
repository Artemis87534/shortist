import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient
from src.database import Base, get_db
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """Создание и удаление тестовой БД."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Сессия БД для unit-тестов."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def client():
    """HTTPX клиент с подменой зависимостей."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def future_expire():
    """Возвращает дату истечения ссылки на 1 день вперёд."""
    return (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat()

@pytest.fixture
async def registered_user(client, future_expire):
    """Создаёт пользователя и возвращает заголовок с токеном."""
    await client.post("/auth/register", json={
        "id": 1,
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    resp = await client.post("/auth/jwt/login", data={
        "username": "user@example.com",
        "password": "string",
        "grant_type": "password"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}