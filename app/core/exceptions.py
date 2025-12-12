"""
Custom Exception Classes

Defines custom exceptions for the application with appropriate HTTP status codes.
Following FastShip pattern for centralized error handling.
"""

from fastapi import status


class LogixpressException(Exception):
    """Base exception for LOGIXPress API"""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class EntityNotFound(LogixpressException):
    """Raised when an entity is not found in the database"""

    def __init__(self, entity_name: str, entity_id: int | str):
        detail = f"{entity_name} with id {entity_id} not found"
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class InvalidCredentials(LogixpressException):
    """Raised when authentication credentials are invalid"""

    def __init__(self):
        detail = "Incorrect username or password"
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class InvalidToken(LogixpressException):
    """Raised when JWT token is invalid or expired"""

    def __init__(self):
        detail = "Could not validate credentials"
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class InsufficientPermissions(LogixpressException):
    """Raised when user doesn't have required permissions"""

    def __init__(self, required_roles: list[str]):
        detail = f"Access denied. Required roles: {', '.join(required_roles)}"
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class InvalidStatusTransition(LogixpressException):
    """Raised when shipment status transition is invalid"""

    def __init__(self, current_status: str, new_status: str, valid_next: str):
        detail = f"Invalid status transition from '{current_status}' to '{new_status}'. Valid next status: {valid_next}"
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class DuplicateEntity(LogixpressException):
    """Raised when trying to create a duplicate entity"""

    def __init__(self, entity_name: str, field: str):
        detail = f"{entity_name} with this {field} already exists"
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class ValidationError(LogixpressException):
    """Raised when validation fails"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_422_UNPROCESSABLE_ENTITY)
