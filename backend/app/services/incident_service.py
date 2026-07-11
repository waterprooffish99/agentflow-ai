import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Incident, IncidentSeverity, IncidentStatus

class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_incident(
        self,
        title: str,
        description: str,
        component: str,
        severity: IncidentSeverity = IncidentSeverity.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Incident:
        incident = Incident(
            title=title,
            description=description,
            component=component,
            severity=severity,
            metadata_json=metadata or {}
        )
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def resolve_incident(self, incident_id: uuid.UUID, user_id: uuid.UUID) -> Incident:
        incident = await self.db.get(Incident, incident_id)
        if incident:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.now(timezone.utc)
            incident.resolved_by = user_id
            await self.db.commit()
            await self.db.refresh(incident)
        return incident

    async def list_active_incidents(self) -> List[Incident]:
        stmt = select(Incident).where(Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]))
        result = await self.db.execute(stmt)
        return result.scalars().all()
