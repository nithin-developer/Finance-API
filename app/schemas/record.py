import uuid
from datetime import date as date_type, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.financial_record import RecordType


class RecordCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    type: RecordType
    category: str = Field(min_length=2, max_length=100)
    date: date_type
    notes: str | None = Field(default=None, max_length=2000)


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    date: date_type | None = None
    notes: str | None = Field(default=None, max_length=2000)


class RecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    type: RecordType
    category: str
    date: date_type
    notes: str | None
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    page: int
    limit: int
    total: int
    total_pages: int
