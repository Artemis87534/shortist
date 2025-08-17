import pytest
import uuid

@pytest.mark.asyncio
async def test_register_and_login(client):
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

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    first = await client.post("/auth/register", json={
        "id": 1,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert first.status_code in (200, 201)
    second = await client.post("/auth/register", json={
        "id": 2,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert second.status_code >= 400