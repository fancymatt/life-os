"""Authentication Models

Data models for user authentication and authorization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    """User model as stored in database"""
    hashed_password: str
    created_at: datetime
    last_login: Optional[datetime] = None


class User(UserBase):
    """User model for responses (no password)"""
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    username: Optional[str] = None
    exp: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str
