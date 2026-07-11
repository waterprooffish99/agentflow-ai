from enum import Enum
from typing import Dict, List

from pydantic import BaseModel


class SubscriptionTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class PlanQuotas(BaseModel):
    monthly_tokens: int
    daily_tokens: int
    monthly_bookings: int
    max_contacts: int
    features: List[str]
    price_monthly: float


PLANS: Dict[SubscriptionTier, PlanQuotas] = {
    SubscriptionTier.FREE: PlanQuotas(
        monthly_tokens=50000,
        daily_tokens=2000,
        monthly_bookings=10,
        max_contacts=50,
        features=["basic_chat"],
        price_monthly=0.0,
    ),
    SubscriptionTier.STARTER: PlanQuotas(
        monthly_tokens=200000,
        daily_tokens=10000,
        monthly_bookings=50,
        max_contacts=500,
        features=["basic_chat", "analytics", "email_notifications"],
        price_monthly=29.0,
    ),
    SubscriptionTier.GROWTH: PlanQuotas(
        monthly_tokens=1000000,
        daily_tokens=50000,
        monthly_bookings=250,
        max_contacts=5000,
        features=[
            "basic_chat",
            "analytics",
            "email_notifications",
            "crm_integration",
            "custom_prompts",
        ],
        price_monthly=99.0,
    ),
    SubscriptionTier.ENTERPRISE: PlanQuotas(
        monthly_tokens=10000000,
        daily_tokens=500000,
        monthly_bookings=10000,
        max_contacts=100000,
        features=["*"],  # All features
        price_monthly=499.0,
    ),
}


def get_plan(tier: str | SubscriptionTier) -> PlanQuotas:
    if isinstance(tier, str):
        try:
            tier = SubscriptionTier(tier.lower())
        except ValueError:
            tier = SubscriptionTier.FREE
    return PLANS.get(tier, PLANS[SubscriptionTier.FREE])
