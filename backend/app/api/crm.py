import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_tenant_id
from app.core.sanitization import sanitize_text
from app.models import Appointment, Lead
from app.schemas.appointment import AppointmentResponse
from app.services.crm_service import ActivityTimelineService, CustomerService
from app.services.follow_up_service import FollowUpService
from app.services.lead_pipeline_service import LeadPipelineService
from sqlalchemy import select

router = APIRouter(prefix="/crm", tags=["crm"])
...
@router.get("/pipeline/history")
async def get_pipeline_history(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # This was previously incorrectly named in my plan, let's just add the leads to the stages
    pass

@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Appointment).where(Appointment.tenant_id == tenant_id).order_by(Appointment.start_time.asc())
    )
    return result.scalars().all()

@router.get("/pipeline", response_model=list[dict])
async def get_full_pipeline(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    from app.models import Customer
    service = LeadPipelineService(db)
    stages = await service.get_stages(tenant_id)
    
    results = []
    for stage in stages:
        leads_res = await db.execute(
            select(Lead, Customer.name)
            .join(Customer, Lead.customer_id == Customer.id)
            .where(Lead.tenant_id == tenant_id, Lead.status.ilike(f"%{stage.name}%")) 
        )
        leads = leads_res.all()
        results.append({
            "id": str(stage.id),
            "name": stage.name,
            "leads": [
                {
                    "id": str(l.Lead.id),
                    "name": l.name,
                    "service": l.Lead.preferred_service or "General",
                    "urgency": l.Lead.urgency or "medium"
                } for l in leads
            ]
        })
    return results


class CustomerNoteRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


@router.get("/customers")
async def list_customers(
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = CustomerService(db)
    return await service.list_customers(tenant_id, limit, offset, search)


@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer or customer.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/customers/{customer_id}/timeline")
async def get_customer_timeline(
    customer_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ActivityTimelineService(db)
    cust_service = CustomerService(db)
    customer = await cust_service.get_customer(customer_id)
    if not customer or customer.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    return await service.get_timeline(customer_id, limit)


@router.post("/customers/{customer_id}/notes")
async def create_customer_note(
    customer_id: uuid.UUID,
    payload: CustomerNoteRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = CustomerService(db)
    return await service.create_note(tenant_id, customer_id, sanitize_text(payload.content))


@router.get("/followups")
async def list_followups(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = FollowUpService(db)
    return await service.list_pending_tasks(tenant_id)


@router.get("/pipeline/stages")
async def list_pipeline_stages(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = LeadPipelineService(db)
    return await service.get_stages(tenant_id)


@router.post("/pipeline/move")
async def move_lead_stage(
    lead_id: uuid.UUID,
    stage_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = LeadPipelineService(db)
    success = await service.move_lead_to_stage(tenant_id, lead_id, stage_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to move lead")
    return {"status": "success"}


@router.get("/pipeline/leads/{lead_id}/history")
async def get_lead_movement_history(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = LeadPipelineService(db)
    return await service.get_lead_history(tenant_id, lead_id)
