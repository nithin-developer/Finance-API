import pytest


@pytest.mark.anyio
async def test_viewer_can_only_access_dashboard(client, create_user_and_login):
    viewer_headers, _ = await create_user_and_login(
        name="Viewer User",
        email="viewer@example.com",
        password="Viewer@12345",
        role="viewer",
    )

    records_response = await client.get("/records", headers=viewer_headers)
    dashboard_response = await client.get("/dashboard/summary", headers=viewer_headers)

    assert records_response.status_code == 403
    assert dashboard_response.status_code == 200


@pytest.mark.anyio
async def test_analyst_has_read_only_record_access(client, create_user_and_login):
    analyst_headers, _ = await create_user_and_login(
        name="Analyst User",
        email="analyst@example.com",
        password="Analyst@12345",
        role="analyst",
    )

    write_response = await client.post(
        "/records",
        headers=analyst_headers,
        json={
            "amount": "100.00",
            "type": "expense",
            "category": "Office",
            "date": "2026-01-10",
            "notes": "Denied write",
        },
    )
    read_response = await client.get("/records", headers=analyst_headers)

    assert write_response.status_code == 403
    assert read_response.status_code == 200
