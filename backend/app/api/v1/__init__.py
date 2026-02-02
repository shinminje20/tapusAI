"""API v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import waitlist_router

router = APIRouter(prefix="/api/v1")
router.include_router(waitlist_router)
