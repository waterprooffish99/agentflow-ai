import uuid
import random
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Experiment, TenantExperimentAssignment, ExperimentStatus

class ExperimentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_variant(self, tenant_id: uuid.UUID, experiment_name: str) -> Optional[str]:
        """Assign or retrieve a variant for a tenant in a specific experiment."""
        # 1. Check existing assignment
        assignment_stmt = select(TenantExperimentAssignment).where(
            TenantExperimentAssignment.tenant_id == tenant_id,
            TenantExperimentAssignment.experiment_name == experiment_name
        )
        assignment = (await self.db.execute(assignment_stmt)).scalar_one_or_none()
        if assignment:
            return assignment.variant_name

        # 2. Check experiment rules
        exp_stmt = select(Experiment).where(Experiment.name == experiment_name)
        exp = (await self.db.execute(exp_stmt)).scalar_one_or_none()
        
        if not exp or exp.status != ExperimentStatus.ACTIVE:
            return None
            
        tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
        tenant = (await self.db.execute(tenant_stmt)).scalar_one()
        
        if exp.target_tiers and tenant.subscription_tier not in exp.target_tiers:
            return None
            
        # 3. Deterministic assignment logic
        random.seed(str(tenant_id) + experiment_name)
        if random.randint(1, 100) > exp.target_percentage:
            return None
            
        # Select variant (uniform distribution for now)
        variant_names = list(exp.variants.keys())
        if not variant_names:
            return None
            
        assigned_variant = random.choice(variant_names)
        
        # 4. Persist assignment
        new_assignment = TenantExperimentAssignment(
            tenant_id=tenant_id,
            experiment_name=experiment_name,
            variant_name=assigned_variant
        )
        self.db.add(new_assignment)
        await self.db.commit()
        
        return assigned_variant

    async def create_experiment(self, name: str, variants: Dict[str, Any], percentage: int = 0) -> Experiment:
        exp = Experiment(name=name, variants=variants, target_percentage=percentage, status=ExperimentStatus.ACTIVE)
        self.db.add(exp)
        await self.db.commit()
        await self.db.refresh(exp)
        return exp
