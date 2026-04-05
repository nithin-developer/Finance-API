from decimal import Decimal

import pytest


@pytest.mark.anyio
async def test_records_filters_pagination_search_and_soft_delete(client, admin_headers):
    payloads = [
        {
            "amount": "1200.00",
            "type": "income",
            "category": "Salary",
            "date": "2026-01-01",
            "notes": "January salary",
        },
        {
            "amount": "800.00",
            "type": "expense",
            "category": "Rent",
            "date": "2026-01-02",
            "notes": "Apartment rent",
        },
        {
            "amount": "200.00",
            "type": "expense",
            "category": "Food",
            "date": "2026-01-03",
            "notes": "Grocery market",
        },
    ]

    record_ids = []
    for payload in payloads:
        response = await client.post("/records", headers=admin_headers, json=payload)
        assert response.status_code == 201
        record_ids.append(response.json()["id"])

    page_response = await client.get("/records?page=1&limit=2", headers=admin_headers)
    assert page_response.status_code == 200
    page_body = page_response.json()
    assert page_body["total"] == 3
    assert page_body["limit"] == 2
    assert page_body["total_pages"] == 2
    assert len(page_body["items"]) == 2

    expense_response = await client.get("/records?type=expense", headers=admin_headers)
    assert expense_response.status_code == 200
    assert expense_response.json()["total"] == 2

    search_response = await client.get("/records?q=rent", headers=admin_headers)
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1
    assert search_response.json()["items"][0]["category"] == "Rent"

    delete_response = await client.delete(f"/records/{record_ids[0]}", headers=admin_headers)
    assert delete_response.status_code == 200

    after_delete = await client.get("/records", headers=admin_headers)
    assert after_delete.status_code == 200
    assert after_delete.json()["total"] == 2

    amounts = [Decimal(item["amount"]) for item in after_delete.json()["items"]]
    assert Decimal("1200.00") not in amounts
