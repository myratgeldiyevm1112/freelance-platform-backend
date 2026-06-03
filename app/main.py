from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.infrastructure.database.session import engine
from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import logging_middleware
from starlette.middleware.base import BaseHTTPMiddleware

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
    description="""
## 🚀 Freelance Platform API

A clean, production-grade REST API for a freelance marketplace.

### Features
- **Auth** — JWT-based registration, login, token refresh
- **Jobs** — Create and browse job postings with filters and pagination
- **Proposals** — Submit and manage proposals on jobs
- **Contracts** — Auto-created on proposal acceptance, lifecycle management
- **Reviews** — Leave reviews after contract completion, rating aggregation

### Auth
Use the **Authorize** button with your `Bearer <token>` to access protected endpoints.
    """,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    contact={
        "name": "Muhammet Myratgeldiyev",
        "url": "https://github.com/myratgeldiyevm1112",
    },
    license_info={
        "name": "MIT",
    },
)

register_exception_handlers(app)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)
app.include_router(api_router)

@app.get("/health", tags=["System"])
async def health_check():
    logger.info("Health check called")
    return {"status": "ok", "env": settings.APP_ENV}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi