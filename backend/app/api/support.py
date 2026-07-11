import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models import SupportIssue, User, UserRole
from app.schemas.support import SupportIssueCreate, SupportIssueResponse, SupportIssueUpdate

router = APIRouter(prefix="/support", tags=["support"])

@router.post("/issues", response_model=SupportIssueResponse)
async def create_issue(
    data: SupportIssueCreate,
    db: deps.DBSession,
    current_user: User = Depends(deps.get_current_user),
):
    """Create a new support issue or feedback."""
    issue = SupportIssue(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        issue_type=data.issue_type,
        title=data.title,
        description=data.description,
        priority=data.priority,
        category=data.category,
        metadata_json=data.metadata_json,
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue

@router.get("/issues", response_model=List[SupportIssueResponse])
async def list_issues(
    db: deps.DBSession,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tenant_id: uuid.UUID = Depends(deps.get_tenant_id),
    current_user: User = Depends(deps.get_current_user),
):
    """List all support issues for a tenant."""
    query = select(SupportIssue).where(SupportIssue.tenant_id == tenant_id)
    if status:
        query = query.where(SupportIssue.status == status)
    if priority:
        query = query.where(SupportIssue.priority == priority)
        
    query = query.order_by(SupportIssue.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/admin/issues", response_model=List[SupportIssueResponse])
async def list_all_issues(
    db: deps.DBSession,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """List all support issues across the platform (Super Admin). Support queue prioritization."""
    query = select(SupportIssue)
    if status:
        query = query.where(SupportIssue.status == status)
    if priority:
        query = query.where(SupportIssue.priority == priority)
        
    # Prioritize by: status (open first), then priority (urgent first), then created_at (oldest first)
    query = query.order_by(SupportIssue.status.asc(), SupportIssue.priority.asc(), SupportIssue.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/issues/{issue_id}", response_model=SupportIssueResponse)
async def get_issue(
    issue_id: uuid.UUID,
    db: deps.DBSession,
    tenant_id: uuid.UUID = Depends(deps.get_tenant_id),
):
    """Get details of a specific support issue."""
    query = select(SupportIssue).where(
        SupportIssue.id == issue_id, 
        SupportIssue.tenant_id == tenant_id
    )
    result = await db.execute(query)
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

# Admin endpoints for support management
@router.patch("/issues/{issue_id}", response_model=SupportIssueResponse)
async def update_issue(
    issue_id: uuid.UUID,
    data: SupportIssueUpdate,
    db: deps.DBSession,
    admin: User = Depends(deps.require_role(UserRole.SUPER_ADMIN)),
):
    """Update support issue status or priority (Super Admin only)."""
    issue = await db.get(SupportIssue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)
        
    await db.commit()
    await db.refresh(issue)
    return issue
