"""
Authentication Router

Endpoints for user authentication and registration.
"""

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser
from app.api.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, User
from app.core.exceptions import InvalidCredentials
from app.core.security import Token
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    **Login Endpoint**

    Authenticate user and receive JWT access token.

    **Test Credentials:**
    - Admin: `admin` / `admin123`
    - Courier: `courier` / `courier123`
    - Customer: `customer` / `customer123`
    """
    user = AuthService.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise InvalidCredentials()

    access_token = AuthService.create_access_token_for_user(user)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest):
    """
    **Sign Up / Register Endpoint**

    Create a new user account.

    **Request Body:**
    - `username`: Unique username (required)
    - `email`: Valid email address (required)
    - `password`: Password with minimum 6 characters (required)
    - `role`: User role - `customer` (default), `courier`, or `admin` (optional)

    **Validation Rules:**
    - Username must be unique
    - Email must be unique and valid format
    - Password must be at least 6 characters
    - Role must be one of: `customer`, `courier`, `admin`

    **Default Behavior:**
    - If role is not specified, user will be registered as `customer`
    - New account is automatically enabled (not disabled)

    **Example:**
    ```json
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password": "securepass123",
      "role": "customer"
    }
    ```
    """
    new_user = AuthService.register_user(register_data)

    return RegisterResponse(
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        message=f"User '{new_user.username}' registered successfully with role '{new_user.role}'",
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: CurrentUser):
    """
    **Get Current User Info**

    Retrieve information about the currently authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return current_user
