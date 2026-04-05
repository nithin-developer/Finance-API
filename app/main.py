from contextlib import asynccontextmanager
from datetime import datetime
from time import timezone

from fastapi import FastAPI
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.security import get_password_hash
from app.db import database
from app.models.user import User, UserRole
from app.routes import auth, dashboard, records, users

settings = get_settings()


async def ensure_first_admin() -> None:
    runtime_settings = get_settings()
    if not runtime_settings.first_admin_password:
        return

    async with database.SessionLocal() as session:
        existing = await session.execute(
            select(User).where(
                User.role == UserRole.admin,
                User.is_deleted.is_(False),
            )
        )
        if existing.scalar_one_or_none():
            return

        admin = User(
            name=runtime_settings.first_admin_name,
            email=runtime_settings.first_admin_email,
            password_hash=get_password_hash(runtime_settings.first_admin_password),
            role=UserRole.admin,
            is_active=True,
        )
        session.add(admin)
        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    runtime_settings = get_settings()
    if runtime_settings.auto_create_tables:
        await database.init_models()
    await ensure_first_admin()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "app_name": settings.app_name, "environment": settings.environment, "timestamp": datetime.now().isoformat()}
