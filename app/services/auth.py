"""
Authentication Service

Business logic for user authentication, registration, and management.
Handles user database operations and authentication workflows.
"""

from datetime import timedelta
from typing import Optional

from app.api.schemas.auth import RegisterRequest, User, UserInDB
from app.config import settings
from app.core.exceptions import DuplicateEntity, ValidationError
from app.core.security import create_access_token, get_password_hash, verify_password

# In-memory user database (for demonstration)
# In production, this would be replaced with actual database
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@logixpress.com",
        "plain_password": "admin123",
        "role": "admin",
        "disabled": False,
    },
    "courier": {
        "username": "courier",
        "email": "courier@logixpress.com",
        "plain_password": "courier123",
        "role": "courier",
        "disabled": False,
    },
    "customer": {
        "username": "customer",
        "email": "customer@example.com",
        "plain_password": "customer123",
        "role": "customer",
        "disabled": False,
    },
}

# Hash passwords on module load
for user_data in fake_users_db.values():
    if "plain_password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data["plain_password"])
        del user_data["plain_password"]


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def get_user(username: str) -> Optional[UserInDB]:
        """
        Get user by username

        Args:
            username: Username to lookup

        Returns:
            UserInDB if found, None otherwise
        """
        if username in fake_users_db:
            user_dict = fake_users_db[username].copy()
            # Convert plain_password to hashed_password if needed (for testing compatibility)
            if "plain_password" in user_dict:
                user_dict["hashed_password"] = get_password_hash(user_dict.pop("plain_password"))
            return UserInDB(**user_dict)
        return None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with username and password

        Args:
            username: Username
            password: Plain text password

        Returns:
            UserInDB if authentication successful, None otherwise
        """
        user = AuthService.get_user(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token_for_user(user: UserInDB) -> str:
        """
        Create JWT access token for a user

        Args:
            user: User to create token for

        Returns:
            JWT access token string
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        return access_token

    @staticmethod
    def register_user(register_data: RegisterRequest) -> User:
        """
        Register a new user

        Args:
            register_data: User registration data

        Returns:
            Created user

        Raises:
            DuplicateEntity: If username or email already exists
            ValidationError: If validation fails
        """
        # Validate role
        valid_roles = ["admin", "courier", "customer"]
        if register_data.role not in valid_roles:
            raise ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")

        # Check if username already exists
        if register_data.username in fake_users_db:
            raise DuplicateEntity("User", "username")

        # Check if email already exists
        for user_data in fake_users_db.values():
            if user_data.get("email") == register_data.email:
                raise DuplicateEntity("User", "email")

        # Validate password strength (minimum 6 characters)
        if len(register_data.password) < 6:
            raise ValidationError("Password must be at least 6 characters long")

        # Create new user
        hashed_password = get_password_hash(register_data.password)
        fake_users_db[register_data.username] = {
            "username": register_data.username,
            "email": register_data.email,
            "hashed_password": hashed_password,
            "role": register_data.role,
            "disabled": False,
        }

        return User(username=register_data.username, email=register_data.email, role=register_data.role, disabled=False)
