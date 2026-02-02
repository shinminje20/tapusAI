"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.v1 import router as api_v1_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Health check endpoint
    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    # Include API routers
    app.include_router(api_v1_router)

    return app


app = create_app()
