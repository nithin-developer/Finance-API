from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType

ZERO = Decimal("0.00")


async def get_summary(db: AsyncSession) -> tuple[Decimal, Decimal, Decimal]:
    income_case = case(
        (FinancialRecord.type == RecordType.income, FinancialRecord.amount),
        else_=0,
    )
    expense_case = case(
        (FinancialRecord.type == RecordType.expense, FinancialRecord.amount),
        else_=0,
    )

    result = await db.execute(
        select(
            func.coalesce(func.sum(income_case), 0),
            func.coalesce(func.sum(expense_case), 0),
        ).where(FinancialRecord.is_deleted.is_(False))
    )
    income, expense = result.one()

    total_income = Decimal(income or 0)
    total_expense = Decimal(expense or 0)
    net_balance = total_income - total_expense

    return total_income, total_expense, net_balance


async def get_category_breakdown(
    db: AsyncSession,
    *,
    record_type: RecordType | None = RecordType.expense,
) -> list[tuple[str, Decimal]]:
    query = (
        select(FinancialRecord.category, func.coalesce(func.sum(FinancialRecord.amount), 0))
        .where(FinancialRecord.is_deleted.is_(False))
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
    )

    if record_type:
        query = query.where(FinancialRecord.type == record_type)

    result = await db.execute(query)
    rows = result.all()
    return [(category, Decimal(total or 0)) for category, total in rows]


async def get_monthly_trends(db: AsyncSession) -> list[dict]:
    income_case = case(
        (FinancialRecord.type == RecordType.income, FinancialRecord.amount),
        else_=0,
    )
    expense_case = case(
        (FinancialRecord.type == RecordType.expense, FinancialRecord.amount),
        else_=0,
    )

    year_expr = func.extract("year", FinancialRecord.date)
    month_expr = func.extract("month", FinancialRecord.date)

    result = await db.execute(
        select(
            year_expr.label("year"),
            month_expr.label("month"),
            func.coalesce(func.sum(income_case), 0).label("income"),
            func.coalesce(func.sum(expense_case), 0).label("expense"),
        )
        .where(FinancialRecord.is_deleted.is_(False))
        .group_by(year_expr, month_expr)
        .order_by(year_expr, month_expr)
    )

    items = []
    for year, month, income, expense in result.all():
        year_num = int(year)
        month_num = int(month)
        label = datetime(year_num, month_num, 1).strftime("%b %Y")
        items.append(
            {
                "month": label,
                "income": Decimal(income or 0),
                "expense": Decimal(expense or 0),
            }
        )
    return items


async def get_recent_transactions(db: AsyncSession, *, limit: int = 5) -> list[FinancialRecord]:
    result = await db.execute(
        select(FinancialRecord)
        .where(FinancialRecord.is_deleted.is_(False))
        .order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
