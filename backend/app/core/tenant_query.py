import uuid

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession


def tenant_select(model: type, tenant_id: uuid.UUID) -> Select:
    return select(model).where(model.tenant_id == tenant_id)


async def tenant_get_or_none(
    db: AsyncSession,
    model: type,
    entity_id: uuid.UUID,
    tenant_id: uuid.UUID,
):
    stmt = select(model).where(model.id == entity_id, model.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
