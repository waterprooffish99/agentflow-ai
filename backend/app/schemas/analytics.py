import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DateRange(BaseModel):
    start_date: Optional[dt.datetime] = None
    end_date: Optional[dt.datetime] = None

class TenantMetric(BaseModel):
    tenant_id: uuid.UUID
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ActivationMetrics(BaseModel):
    tenant_id: uuid.UUID
    time_to_first_value_hours: Optional[float] = None
    onboarding_completion_pct: float
    is_activated: bool
    bottlenecks: List[str] = Field(default_factory=list)

class RetentionMetrics(BaseModel):
    tenant_id: uuid.UUID
    cohort_month: str
    active_days_last_30: int
    churn_risk: str # LOW, MEDIUM, HIGH
    engagement_trend: float # Week-over-week delta

class SupportMetrics(BaseModel):
    tenant_id: Optional[uuid.UUID] = None # Optional for global metrics
    open_issues_count: int
    avg_resolution_time_hours: Optional[float] = None
    top_issue_categories: List[Dict[str, Any]] = Field(default_factory=list)

class ConversionMetrics(BaseModel):
    tenant_id: uuid.UUID
    current_tier: str
    conversion_probability: float
    trial_days_remaining: Optional[int] = None

class PMFInsights(BaseModel):
    vertical: Optional[str] = None
    retention_correlation: float
    top_features: List[str] = Field(default_factory=list)

class OperationalAnomaly(BaseModel):
    anomaly_type: str
    severity: str # INFO, WARNING, CRITICAL
    detected_at: dt.datetime
    description: str
