# Schemas barrel export
from app.schemas.auth import (
    EmailVerifyRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    UserInviteRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.base import ErrorResponse, PaginatedResponse, PaginationMeta
from app.schemas.tenant import (
    PlatformMetrics,
    TenantListItem,
    TenantResponse,
    TenantUpdateRequest,
)
from app.schemas.lead import (
    CustomerResponse,
    LeadAssignRequest,
    LeadCreateRequest,
    LeadDetailResponse,
    LeadNoteRequest,
    LeadResponse,
    LeadUpdateRequest,
    LeadWithCustomer,
)
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentRescheduleRequest,
    AppointmentUpdateRequest,
    AvailabilityResponse,
    TimeSlot,
)
from app.schemas.conversation import (
    AIMetrics,
    AnalyticsDashboard,
    ConversationDetailResponse,
    ConversationResponse,
    EscalateRequest,
    Message,
    WidgetMessageRequest,
    WidgetMessageResponse,
)
from app.schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowDetailResponse,
    WorkflowExecutionResponse,
    WorkflowResponse,
    WorkflowTriggerRequest,
    WorkflowUpdateRequest,
)
from app.schemas.correction import (
    CorrectionResponse,
    CorrectionCreate,
    CorrectionReviewRequest,
)
from app.schemas.permission_policy import (
    PermissionPolicyResponse,
    PermissionPolicyUpdateRequest,
)

__all__ = [
    # Auth
    "UserRegisterRequest",
    "UserRegisterResponse",
    "EmailVerifyRequest",
    "UserLoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "RefreshResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "UserResponse",
    "UserUpdateRequest",
    "UserInviteRequest",
    # Base
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    # Tenant
    "TenantResponse",
    "TenantUpdateRequest",
    "TenantListItem",
    "PlatformMetrics",
    # Lead
    "LeadResponse",
    "LeadCreateRequest",
    "LeadUpdateRequest",
    "LeadNoteRequest",
    "LeadAssignRequest",
    "CustomerResponse",
    "LeadWithCustomer",
    "LeadDetailResponse",
    # Appointment
    "AppointmentCreateRequest",
    "AppointmentResponse",
    "AppointmentUpdateRequest",
    "AppointmentCancelRequest",
    "AppointmentRescheduleRequest",
    "AvailabilityResponse",
    "TimeSlot",
    # Conversation
    "ConversationResponse",
    "Message",
    "ConversationDetailResponse",
    "EscalateRequest",
    "WidgetMessageRequest",
    "WidgetMessageResponse",
    "AnalyticsDashboard",
    "AIMetrics",
    # Workflow
    "WorkflowCreateRequest",
    "WorkflowUpdateRequest",
    "WorkflowTriggerRequest",
    "WorkflowResponse",
    "WorkflowExecutionResponse",
    "WorkflowDetailResponse",
    # Support
    "SupportIssueCreate",
    "SupportIssueUpdate",
    "SupportIssueResponse",
    # Correction
    "CorrectionResponse",
    "CorrectionCreate",
    "CorrectionReviewRequest",
    # PermissionPolicy
    "PermissionPolicyResponse",
    "PermissionPolicyUpdateRequest",
]

from app.schemas.support import (
    SupportIssueCreate,
    SupportIssueResponse,
    SupportIssueUpdate,
)