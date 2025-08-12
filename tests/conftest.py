import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient
from src.database import Base, get_db
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///file:tests_db?mode=memory&cache=shared&uri=true"

@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, future=True)
    try:
        yield eng
    finally:
        await eng.dispose()

@pytest.fixture(scope="session", autouse=True)
async def prepare_database(engine):
    """Create/drop tables once per test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_session_maker(engine):
    return async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture
async def db_session(async_session_maker) -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def client(async_session_maker):
    async def override_get_db():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def future_expire():
    return (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat()

@pytest.fixture
async def registered_user(client, future_expire):
    """Register a user and return Authorization header dict.
    Note: UserCreate in the project requires 'id' in the payload, so we provide it.
    """
    resp = await client.post("/auth/register", json={
        "id": 1,
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert resp.status_code in (200, 201), f"Register failed: {resp.status_code} {resp.text}"
    login = await client.post("/auth/jwt/login", data={
        "username": "user@example.com",
        "password": "string",
        "grant_type": "password"
    })
    assert login.status_code == 200, f"Login failed: {login.status_code} {login.text}"
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}