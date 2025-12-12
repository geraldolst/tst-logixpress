"""
API Dependencies

FastAPI dependency injection for authentication, authorization, and services.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import security, decode_access_token
from app.core.exceptions import InvalidToken, InsufficientPermissions
from app.api.schemas.auth import User
from app.services.auth import AuthService
from app.services.shipment import ShipmentService


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Current user
        
    Raises:
        InvalidToken: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None:
        raise InvalidToken()
    
    user = AuthService.get_user(username=token_data.username)
    if user is None:
        raise InvalidToken()
    
    # Convert UserInDB to User (remove password hash)
    return User(
        username=user.username,
        email=user.email,
        role=user.role,
        disabled=user.disabled
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure user is active
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to check if user has required role
    
    Args:
        allowed_roles: List of allowed roles
        
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissions(allowed_roles)
        return current_user
    return role_checker


# Service dependencies (for dependency injection)
def get_auth_service() -> AuthService:
    """Get authentication service instance"""
    return AuthService()


def get_shipment_service() -> ShipmentService:
    """Get shipment service instance"""
    return ShipmentService()


# Type annotations for dependencies
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
