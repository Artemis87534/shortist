import os
import uuid
import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database import Base, get_db

os.environ.setdefault("SECRET", "test-secret")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture
async def async_session_maker(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

@pytest.fixture
async def db_session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def client(async_session_maker) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def future_expire() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat()

@pytest.fixture
async def registered_user(client) -> dict:
    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post("/auth/register", json={
        "id": 1,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert resp.status_code in (200, 201)
    login = await client.post("/auth/jwt/login", data={
        "username": email,
        "password": "string",
        "grant_type": "password"
    })
    assert login.status_code in (200, 204)
    set_cookie = login.headers.get("set-cookie", "")
    assert "shortist=" in set_cookie.lower()
    return {"email": email}