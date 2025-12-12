"""
LOGIXPress API - Main Application Entry Point

Last-Mile Delivery System - Shipment Lifecycle Management API
Domain-Driven Design (DDD) Implementation

Author: Geraldo Linggom Samuel Tampubolon (18223136)
Course: TST (Teknologi Sistem Terintegrasi) - ITB
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.config import settings
from app.api.router import api_router


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "LOGIXPress API - Shipment Lifecycle Management",
        "version": settings.APP_VERSION,
        "bounded_context": "Shipment Lifecycle Management (Core Domain)",
        "docs": settings.DOCS_URL,
        "scalar_docs": "/scalar"
    }


# Scalar API documentation endpoint
@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    """Alternative API documentation using Scalar"""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=settings.APP_NAME,
    )
