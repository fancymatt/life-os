"""Authentication Dependencies

FastAPI dependencies for route protection and user authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from api.services.auth_service import auth_service
from api.models.auth import User, TokenData
from api.config import settings


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    # If authentication is disabled, return None (no user required)
    if not settings.require_authentication:
        return None

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = auth_service.verify_token(token, token_type="access")

    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_user(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Convert UserInDB to User (remove hashed_password)
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        created_at=user.created_at,
        last_login=user.last_login
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (ensures user is not disabled)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user

    Raises:
        HTTPException: If user is disabled
    """
    if current_user and current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def optional_authentication(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Optional authentication - returns user if authenticated, None otherwise
    Does not raise exceptions for unauthenticated requests

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User object if authenticated, None otherwise
    """
    if not settings.require_authentication:
        return None

    if credentials is None:
        return None

    token = credentials.credentials
    token_data = auth_service.verify_token(token, token_type="access")

    if token_data is None or token_data.username is None:
        return None

    user = auth_service.get_user(username=token_data.username)
    if user is None or user.disabled:
        return None

    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        created_at=user.created_at,
        last_login=user.last_login
    )
