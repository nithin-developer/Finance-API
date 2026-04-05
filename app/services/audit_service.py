from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def add_audit_log(
    db: AsyncSession,
    user_id,
    action: str,
    details: str | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            details=details,
        )
    )
