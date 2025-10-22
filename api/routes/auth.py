"""Authentication Routes

Endpoints for user authentication, registration, and token management.
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.auth import Token, LoginRequest, UserCreate, User, RefreshTokenRequest
from api.services.auth_service_db import AuthServiceDB
from api.database import get_db
from api.dependencies.auth import get_current_active_user
from api.config import settings


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    User login - returns access and refresh tokens

    Authenticates user credentials and returns JWT tokens for API access.
    """
    auth_service = AuthServiceDB(db)
    user = await auth_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.username}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        refresh_token=refresh_token
    )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    OAuth2 compatible token login

    Standard OAuth2 password flow for compatibility with OAuth2 clients.
    """
    auth_service = AuthServiceDB(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.username}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token

    Exchange a valid refresh token for a new access token.
    """
    auth_service = AuthServiceDB(db)
    token_data = auth_service.verify_token(request.refresh_token, token_type="refresh")

    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user(username=token_data.username)
    if user is None or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user

    Create a new user account. This endpoint may be disabled in production.
    """
    try:
        auth_service = AuthServiceDB(db)
        user = await auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information

    Returns information about the authenticated user.
    """
    return current_user


@router.get("/users", response_model=list[User])
async def list_users(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """
    List all users

    Admin endpoint to list all registered users.
    """
    auth_service = AuthServiceDB(db)
    return await auth_service.list_users()
