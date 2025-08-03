import pytest
from httpx import AsyncClient
from src.auth.models import User
from src.auth.manager import get_user_manager

pytestmark = pytest.mark.asyncio

class TestAuthAPI:
    async def test_successful_registration(self, test_client: AsyncClient):
        """Тест успешной регистрации пользователя"""
        response = await test_client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "strongpassword123",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
        )
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["email"] == "test@example.com"

    async def test_duplicate_email_registration(self, test_client: AsyncClient, test_user: User):
        """Тест регистрации с существующим email"""
        response = await test_client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "anotherpassword123",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
        )
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"].lower()

    async def test_successful_login(self, test_client: AsyncClient, test_user: User):
        """Тест успешного входа"""
        response = await test_client.post(
            "/auth/jwt/login",
            data={
                "username": test_user.email,
                "password": "testpassword"  # Пароль из фикстуры test_user
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_with_wrong_password(self, test_client: AsyncClient, test_user: User):
        """Тест входа с неверным паролем"""
        response = await test_client.post(
            "/auth/jwt/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 400
        assert "invalid credentials" in response.json()["detail"].lower()

    async def test_protected_endpoint_without_token(self, test_client: AsyncClient):
        """Тест доступа к защищенному эндпоинту без токена"""
        response = await test_client.get("/auth/me")
        assert response.status_code == 401

    async def test_successful_current_user_retrieval(self, authenticated_client: AsyncClient):
        """Тест получения данных текущего пользователя"""
        response = await authenticated_client.get("/auth/me")
        assert response.status_code == 200
        assert "email" in response.json()
        assert "id" in response.json()