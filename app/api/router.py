"""
Master Router

Combines all API routers into a single router for the application.
"""

from fastapi import APIRouter

from app.api.routers import auth, shipment, stats, tracking

# Create master API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(shipment.router)
api_router.include_router(tracking.router)
api_router.include_router(stats.router)
