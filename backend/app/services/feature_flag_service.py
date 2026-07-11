import uuid
import random
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, FeatureFlag, TenantFeatureOverride, FeatureStatus

class FeatureFlagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_enabled(self, tenant_id: uuid.UUID, feature_name: str) -> bool:
        """Check if a feature is enabled for a specific tenant."""
        # 1. Check for manual override first
        override_stmt = select(TenantFeatureOverride).where(
            TenantFeatureOverride.tenant_id == tenant_id,
            TenantFeatureOverride.feature_name == feature_name
        )
        override = (await self.db.execute(override_stmt)).scalar_one_or_none()
        if override is not None:
            return override.is_enabled

        # 2. Check global flag
        flag_stmt = select(FeatureFlag).where(FeatureFlag.name == feature_name)
        flag = (await self.db.execute(flag_stmt)).scalar_one_or_none()
        
        if not flag:
            return False
            
        if flag.status == FeatureStatus.ENABLED:
            return True
        if flag.status == FeatureStatus.DISABLED:
            return False
            
        # 3. Staged Rollout logic
        tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
        tenant = (await self.db.execute(tenant_stmt)).scalar_one()
        
        # Check tier
        if flag.allowed_tiers and tenant.subscription_tier not in flag.allowed_tiers:
            return False
            
        # Check percentage
        if flag.rollout_percentage > 0:
            # Deterministic hash of tenant_id for consistent rollout
            random.seed(str(tenant_id) + feature_name)
            if random.randint(1, 100) <= flag.rollout_percentage:
                return True
                
        return False

    async def create_flag(self, name: str, status: FeatureStatus = FeatureStatus.DISABLED, percentage: int = 0) -> FeatureFlag:
        flag = FeatureFlag(name=name, status=status, rollout_percentage=percentage)
        self.db.add(flag)
        await self.db.commit()
        return flag
