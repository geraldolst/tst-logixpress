"""
Application Configuration Module

Centralized configuration management for LOGIXPress API.
Uses environment variables with sensible defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # App Information
    APP_NAME: str = "LOGIXPress API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = """Last-Mile Delivery System - Shipment Lifecycle Management API
    
    Bounded Context: **Shipment Lifecycle Management** (Core Domain)
    
    Sistem ini mengelola siklus hidup pengiriman dari pembuatan order hingga delivered,
    dengan tracking events yang lengkap sesuai prinsip Domain-Driven Design (DDD).
    """
    
    # API Configuration
    API_V1_PREFIX: str = ""
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # JWT Configuration
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Contact Information
    CONTACT_NAME: str = "Geraldo Linggom Samuel Tampubolon"
    CONTACT_EMAIL: str = "geraldo.tampubolon@example.com"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
