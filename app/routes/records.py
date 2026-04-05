import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.dependencies.rbac import require_roles
from app.models.financial_record import FinancialRecord, RecordType
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.record import (
    RecordCreate,
    RecordListResponse,
    RecordResponse,
    RecordUpdate,
)
from app.services.audit_service import add_audit_log
from app.services.record_service import get_record_or_none, list_records

router = APIRouter(prefix="/records", tags=["Records"])


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    payload: RecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.admin])),
) -> RecordResponse:
    record = FinancialRecord(
        user_id=current_user.id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
    )
    db.add(record)
    await add_audit_log(
        db,
        user_id=current_user.id,
        action="record.create",
        details=f"Created {payload.type.value} {payload.amount} in {payload.category}",
    )
    await db.commit()
    await db.refresh(record)
    return RecordResponse.model_validate(record)


@router.get("", response_model=RecordListResponse)
async def get_records(
    type: RecordType | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.analyst, UserRole.admin])),
) -> RecordListResponse:
    items, total, total_pages = await list_records(
        db,
        record_type=type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        q=q,
        page=page,
        limit=limit,
    )

    return RecordListResponse(
        items=[RecordResponse.model_validate(item) for item in items],
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles([UserRole.analyst, UserRole.admin])),
) -> RecordResponse:
    record = await get_record_or_none(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return RecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: uuid.UUID,
    payload: RecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.admin])),
) -> RecordResponse:
    record = await get_record_or_none(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    await add_audit_log(
        db,
        user_id=current_user.id,
        action="record.update",
        details=f"Updated record {record_id}",
    )
    await db.commit()
    await db.refresh(record)
    return RecordResponse.model_validate(record)


@router.delete("/{record_id}", response_model=MessageResponse)
async def delete_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.admin])),
) -> MessageResponse:
    record = await get_record_or_none(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    record.is_deleted = True
    await add_audit_log(
        db,
        user_id=current_user.id,
        action="record.delete",
        details=f"Soft deleted record {record_id}",
    )
    await db.commit()
    return MessageResponse(message="Record deleted successfully")
