import uuid
import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post("/auth/register", json={
        "id": 100,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert resp.status_code in (200, 201)

    resp = await client.post("/auth/jwt/login", data={
        "username": email,
        "password": "string",
        "grant_type": "password"
    })
    assert resp.status_code in (200, 204)
    assert "shortist=" in resp.headers.get("set-cookie", "").lower()

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    first = await client.post("/auth/register", json={
        "id": 200,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert first.status_code in (200, 201)

    second = await client.post("/auth/register", json={
        "id": 201,
        "email": email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert second.status_code == 400