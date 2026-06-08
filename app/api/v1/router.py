from fastapi import APIRouter
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.jobs import router as jobs_router
from app.api.v1.routers.proposals import router as proposals_router
from app.api.v1.routers.contracts import router as contracts_router
from app.api.v1.routers.reviews import router as reviews_router
from app.api.v1.routers.websocket import router as websocket_router
from app.api.v1.routers.skills import router as skills_router
from app.api.v1.routers.messages import router as messages_router
from app.api.v1.routers.payments import router as payments_router
from app.api.v1.routers.notifications import router as notifications_router
from app.api.v1.routers.freelancers import router as freelancers_router
from app.api.v1.routers.disputes import router as disputes_router
from app.api.v1.routers.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(jobs_router)
api_router.include_router(proposals_router)
api_router.include_router(contracts_router)
api_router.include_router(reviews_router)
api_router.include_router(websocket_router)
api_router.include_router(skills_router)
api_router.include_router(messages_router)
api_router.include_router(payments_router)
api_router.include_router(notifications_router)
api_router.include_router(freelancers_router)
api_router.include_router(disputes_router)
api_router.include_router(admin_router)
api_router.include_router(freelancers_router)
api_router.include_router(disputes_router)
api_router.include_router(admin_router)
