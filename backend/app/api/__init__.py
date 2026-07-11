from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.onboarding import router as onboarding_router
from app.api.chat import router as chat_router
from app.api.crm import router as crm_router
from app.api.analytics import router as analytics_router
from app.api.billing import router as billing_router
from app.api.support import router as support_router
from app.api.success import router as success_router
from app.api.corrections import router as corrections_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(onboarding_router)
api_router.include_router(chat_router)
api_router.include_router(crm_router)
api_router.include_router(analytics_router)
api_router.include_router(billing_router)
api_router.include_router(support_router)
api_router.include_router(success_router)
api_router.include_router(corrections_router)

# Future routers to be included:
# from app.api.tenants import router as tenants_router
# from app.api.users import router as users_router
# from app.api.leads import router as leads_router
# ...
