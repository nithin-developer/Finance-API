from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.dependencies.rbac import require_roles
from app.models.financial_record import RecordType
from app.models.user import User, UserRole
from app.schemas.dashboard import (
    CategoryBreakdownItem,
    DashboardSummaryResponse,
    MonthlyTrendItem,
    RecentTransactionsResponse,
)
from app.schemas.record import RecordResponse
from app.services.dashboard_service import (
    get_category_breakdown,
    get_monthly_trends,
    get_recent_transactions,
    get_summary,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.viewer, UserRole.analyst, UserRole.admin])),
) -> DashboardSummaryResponse:
    total_income, total_expense, net_balance = await get_summary(db)
    return DashboardSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
    )


@router.get("/category-breakdown", response_model=list[CategoryBreakdownItem])
async def category_breakdown(
    record_type: RecordType | None = Query(default=RecordType.expense),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.viewer, UserRole.analyst, UserRole.admin])),
) -> list[CategoryBreakdownItem]:
    rows = await get_category_breakdown(db, record_type=record_type)
    return [CategoryBreakdownItem(category=category, total=total) for category, total in rows]


@router.get("/monthly-trends", response_model=list[MonthlyTrendItem])
async def monthly_trends(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.viewer, UserRole.analyst, UserRole.admin])),
) -> list[MonthlyTrendItem]:
    items = await get_monthly_trends(db)
    return [MonthlyTrendItem(**item) for item in items]


@router.get("/recent", response_model=RecentTransactionsResponse)
async def recent_transactions(
    limit: int = Query(default=5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.viewer, UserRole.analyst, UserRole.admin])),
) -> RecentTransactionsResponse:
    items = await get_recent_transactions(db, limit=limit)
    return RecentTransactionsResponse(
        items=[RecordResponse.model_validate(item) for item in items]
    )
