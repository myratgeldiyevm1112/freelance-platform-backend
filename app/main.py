from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.infrastructure.database.session import engine
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.jobs import router as jobs_router
from app.api.v1.routers.proposals import router as proposals_router
from app.api.v1.routers.contracts import router as contracts_router
from app.api.v1.routers.reviews import router as reviews_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting app in {settings.APP_ENV} mode")
    logger.info("Database engine created")
    yield
    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(
    title="Freelance Platform API",
    description="A clean freelance marketplace REST API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    swagger_ui_init_oauth={},
    components={
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            }
        }
    },
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(proposals_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok", "env": settings.APP_ENV}