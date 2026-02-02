"""API v1 endpoints."""

from app.api.v1.endpoints.waitlist import router as waitlist_router

__all__ = ["waitlist_router"]
