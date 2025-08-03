import pytest
from httpx import AsyncClient
from fastapi_users.manager import BaseUserManager
from src.auth.models import User

pytestmark = pytest.mark.asyncio

class TestAuthAPI:
    async def test_successful_registration(self, test_client: AsyncClient):
        """Test user registration"""
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
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_login_flow(self, test_client: AsyncClient):
        """Test complete login flow"""
        # 1. Register
        await test_client.post("/auth/register", json={
            "email": "loginuser@example.com",
            "password": "LoginPass123!",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        })

        # 2. Login
        login_res = await test_client.post(
            "/auth/jwt/login",
            data={
                "username": "loginuser@example.com",
                "password": "LoginPass123!"
            }
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # 3. Access protected endpoint
        token = login_res.json()["access_token"]
        me_res = await test_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "loginuser@example.com"