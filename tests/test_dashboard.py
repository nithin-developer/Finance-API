from decimal import Decimal

import pytest


@pytest.mark.anyio
async def test_dashboard_aggregations(client, admin_headers):
    transactions = [
        {
            "amount": "50000.00",
            "type": "income",
            "category": "Salary",
            "date": "2026-01-10",
            "notes": "Primary salary",
        },
        {
            "amount": "20000.00",
            "type": "expense",
            "category": "Rent",
            "date": "2026-01-11",
            "notes": "Office rent",
        },
        {
            "amount": "5000.00",
            "type": "expense",
            "category": "Food",
            "date": "2026-02-03",
            "notes": "Team food",
        },
    ]

    for payload in transactions:
        response = await client.post("/records", headers=admin_headers, json=payload)
        assert response.status_code == 201

    summary_response = await client.get("/dashboard/summary", headers=admin_headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()

    assert Decimal(str(summary["total_income"])) == Decimal("50000.00")
    assert Decimal(str(summary["total_expense"])) == Decimal("25000.00")
    assert Decimal(str(summary["net_balance"])) == Decimal("25000.00")

    category_response = await client.get("/dashboard/category-breakdown", headers=admin_headers)
    assert category_response.status_code == 200
    category_items = {item["category"]: Decimal(str(item["total"])) for item in category_response.json()}
    assert category_items["Rent"] == Decimal("20000.00")
    assert category_items["Food"] == Decimal("5000.00")

    trends_response = await client.get("/dashboard/monthly-trends", headers=admin_headers)
    assert trends_response.status_code == 200
    trends = trends_response.json()
    assert len(trends) == 2

    recent_response = await client.get("/dashboard/recent?limit=2", headers=admin_headers)
    assert recent_response.status_code == 200
    assert len(recent_response.json()["items"]) == 2
