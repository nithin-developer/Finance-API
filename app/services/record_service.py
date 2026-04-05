from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType


async def list_records(
    db: AsyncSession,
    *,
    record_type: RecordType | None,
    category: str | None,
    start_date: date | None,
    end_date: date | None,
    q: str | None,
    page: int,
    limit: int,
) -> tuple[list[FinancialRecord], int, int]:
    query = select(FinancialRecord).where(FinancialRecord.is_deleted.is_(False))

    if record_type:
        query = query.where(FinancialRecord.type == record_type)
    if category:
        query = query.where(FinancialRecord.category.ilike(f"%{category}%"))
    if start_date:
        query = query.where(FinancialRecord.date >= start_date)
    if end_date:
        query = query.where(FinancialRecord.date <= end_date)
    if q:
        query = query.where(
            or_(
                FinancialRecord.category.ilike(f"%{q}%"),
                FinancialRecord.notes.ilike(f"%{q}%"),
            )
        )

    total_query = select(func.count()).select_from(query.subquery())
    total = int((await db.execute(total_query)).scalar_one())

    offset = (page - 1) * limit
    query = query.order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
    query = query.offset(offset).limit(limit)

    rows = await db.execute(query)
    items = list(rows.scalars().all())
    total_pages = max((total + limit - 1) // limit, 1)

    return items, total, total_pages


async def get_record_or_none(
    db: AsyncSession,
    record_id,
) -> FinancialRecord | None:
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id,
            FinancialRecord.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()
