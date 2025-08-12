import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    resp = await client.post("/auth/register", json={
        "id": 100,
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert resp.status_code in (200, 201), f"register failed: {resp.status_code} {resp.text}"

    resp = await client.post("/auth/jwt/login", data={
        "username": "user@example.com",
        "password": "string",
        "grant_type": "password"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "id": 200,
        "email": "dup@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    resp = await client.post("/auth/register", json={
        "id": 201,
        "email": "dup@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert resp.status_code >= 400