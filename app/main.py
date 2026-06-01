from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, logger

setup_logging()

app = FastAPI(
    title="Freelance Platform API",
    description="A clean freelance marketplace REST API",
    version="0.1.0",
    debug=settings.DEBUG,
)


@app.on_event("startup")
async def startup():
    logger.info(f"Starting app in {settings.APP_ENV} mode")


@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok", "env": settings.APP_ENV}