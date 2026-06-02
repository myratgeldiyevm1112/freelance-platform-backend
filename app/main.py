from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.infrastructure.database.session import engine
from app.api.v1.router import api_router

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

app.include_router(api_router)


@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok", "env": settings.APP_ENV}