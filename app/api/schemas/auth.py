"""
Authentication Schemas

Request and response models for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """User registration request schema"""
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "customer"  # Default role is customer


class RegisterResponse(BaseModel):
    """User registration response schema"""
    username: str
    email: str
    role: str
    message: str


class User(BaseModel):
    """User model for responses"""
    username: str
    email: str
    role: str
    disabled: Optional[bool] = None


class UserInDB(User):
    """User model with password hash (internal use)"""
    hashed_password: str
