from decimal import Decimal

from pydantic import BaseModel

from app.schemas.record import RecordResponse


class DashboardSummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal


class CategoryBreakdownItem(BaseModel):
    category: str
    total: Decimal


class MonthlyTrendItem(BaseModel):
    month: str
    income: Decimal
    expense: Decimal


class RecentTransactionsResponse(BaseModel):
    items: list[RecordResponse]
