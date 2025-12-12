"""
LOGIXPress API - Main Application Entry Point

Last-Mile Delivery System - Shipment Lifecycle Management API
Domain-Driven Design (DDD) Implementation

Author: Geraldo Linggom Samuel Tampubolon (18223136)
Course: TST (Teknologi Sistem Terintegrasi) - ITB
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import (
    DuplicateEntity,
    EntityNotFound,
    InsufficientPermissions,
    InvalidCredentials,
    InvalidStatusTransition,
    InvalidToken,
    ValidationError,
)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    contact={"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
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


# Exception handlers
@app.exception_handler(EntityNotFound)
async def entity_not_found_handler(request: Request, exc: EntityNotFound):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(DuplicateEntity)
async def duplicate_entity_handler(request: Request, exc: DuplicateEntity):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.detail})


@app.exception_handler(InvalidCredentials)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(status_code=401, content={"detail": exc.detail})


@app.exception_handler(InvalidToken)
async def invalid_token_handler(request: Request, exc: InvalidToken):
    return JSONResponse(status_code=401, content={"detail": exc.detail})


@app.exception_handler(InsufficientPermissions)
async def insufficient_permissions_handler(request: Request, exc: InsufficientPermissions):
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(InvalidStatusTransition)
async def invalid_status_transition_handler(request: Request, exc: InvalidStatusTransition):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "LOGIXPress API - Shipment Lifecycle Management",
        "version": settings.APP_VERSION,
        "bounded_context": "Shipment Lifecycle Management (Core Domain)",
        "docs": settings.DOCS_URL,
        "scalar_docs": "/scalar",
    }


# Scalar API documentation endpoint
@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    """Alternative API documentation using Scalar"""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=settings.APP_NAME,
    )
