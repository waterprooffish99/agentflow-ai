import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_tenant_id, get_current_user
from app.models import Correction, User
from app.schemas.correction import CorrectionResponse, CorrectionReviewRequest

router = APIRouter(prefix="/corrections", tags=["corrections"])

@router.get("/pending", response_model=list[CorrectionResponse])
async def list_pending_corrections(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """List unreviewed (pending) corrections for the current tenant."""
    stmt = select(Correction).where(
        Correction.tenant_id == tenant_id,
        Correction.was_edited == None
    ).order_by(Correction.created_at.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{correction_id}/review", response_model=CorrectionResponse)
async def review_correction(
    correction_id: uuid.UUID,
    data: CorrectionReviewRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
):
    """Review and mark a correction as sent as-is or sent edited."""
    stmt = select(Correction).where(
        Correction.id == correction_id,
        Correction.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    correction = result.scalar_one_or_none()
    
    if not correction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correction not found or tenant mismatch"
        )
        
    correction.was_edited = data.was_edited
    if data.was_edited:
        if not data.human_edited_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="human_edited_message must be provided if was_edited is True"
            )
        correction.human_edited_message = data.human_edited_message
    else:
        correction.human_edited_message = None
        
    correction.reviewed_by = current_user.id
    correction.reviewed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(correction)
    return correction
