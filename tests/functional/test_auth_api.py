import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    async def test_successful_registration(self, test_client: AsyncClient):
        response = await test_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"

    async def test_login_flow(self, test_client: AsyncClient):
        await test_client.post("/auth/register", json={
            "email": "loginuser@example.com",
            "password": "LoginPass123!",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        })

        login_res = await test_client.post(
            "/auth/jwt/login",
            data={
                "username": "loginuser@example.com",
                "password": "LoginPass123!"
            }
        )
        assert login_res.status_code == 200
        token = login_res.json().get("access_token")
        assert token

        me_res = await test_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "loginuser@example.com"