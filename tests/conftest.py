import os

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def client(tmp_path):
    db_file = tmp_path / "test.db"

    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    os.environ["AUTO_CREATE_TABLES"] = "true"
    os.environ["FIRST_ADMIN_NAME"] = "System Admin"
    os.environ["FIRST_ADMIN_EMAIL"] = "admin@example.com"
    os.environ["FIRST_ADMIN_PASSWORD"] = "Admin@12345"
    os.environ["SECRET_KEY"] = "test-secret-key"

    from app.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()

    from app.db.database import close_engine, configure_engine

    configure_engine(settings.database_url)

    from app.main import app

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client

    await close_engine()
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin@12345"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def create_user_and_login(client: AsyncClient, admin_headers):
    async def _factory(name: str, email: str, password: str, role: str):
        create_response = await client.post(
            "/auth/register",
            headers=admin_headers,
            json={
                "name": name,
                "email": email,
                "password": password,
                "role": role,
            },
        )
        assert create_response.status_code == 201

        login_response = await client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, create_response.json()

    return _factory
