import pytest


@pytest.mark.anyio
async def test_admin_login_and_me(client, admin_headers):
    me_response = await client.get("/auth/me", headers=admin_headers)

    assert me_response.status_code == 200
    body = me_response.json()
    assert body["email"] == "admin@example.com"
    assert body["role"] == "admin"


@pytest.mark.anyio
async def test_change_password(client, admin_headers):
    response = await client.post(
        "/auth/change-password",
        headers=admin_headers,
        json={
            "current_password": "Admin@12345",
            "new_password": "Admin@12345X",
        },
    )

    assert response.status_code == 200

    relogin = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin@12345X"},
    )
    assert relogin.status_code == 200
