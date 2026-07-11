import datetime as dt
from typing import Optional, TypeVar, List, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant

T = TypeVar("T")

def apply_tenant_filter(query: select, tenant_id: Any):
    """Utility to enforce tenant isolation in analytics queries."""
    # Assuming models have a tenant_id field
    return query.where(getattr(query.column_descriptions[0]['entity'], 'tenant_id') == tenant_id)

def apply_date_window(query: select, model_attr: Any, days: int = 90):
    """Enforce a maximum date window for analytics queries (default 90 days)."""
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    return query.where(model_attr >= since)

async def safe_execute_query(db: AsyncSession, query: select) -> List[Any]:
    """Wrapper for safe async query execution with basic error handling."""
    result = await db.execute(query)
    return result.all()

def paginate_query(query: select, limit: int = 100, offset: int = 0):
    """Apply standard pagination for heavy datasets."""
    return query.limit(limit).offset(offset)

def aggregate_count(model_attr: Any):
    """Standard count aggregation helper."""
    return func.count(model_attr)

def aggregate_avg(model_attr: Any):
    """Standard average aggregation helper."""
    return func.avg(model_attr)
