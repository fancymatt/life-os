"""Authentication Service (PostgreSQL)

Handles user authentication, password hashing, and JWT token management using PostgreSQL.
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from jose import JWTError, jwt

from api.config import settings
from api.models.auth import UserInDB, TokenData, User
from api.models.db import User as DBUser
from api.repositories.user_repository import UserRepository


class AuthServiceDB:
    """Service for authentication and authorization (PostgreSQL-backed)"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    def _truncate_password(self, password: str) -> bytes:
        """
        Truncate password to 72 bytes for bcrypt compatibility

        Bcrypt has a maximum password length of 72 bytes. This method
        automatically truncates longer passwords to prevent errors.

        Args:
            password: Plain text password

        Returns:
            Password as bytes, truncated to 72 bytes if necessary
        """
        # Encode to bytes and truncate to 72 bytes
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return password_bytes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Automatically handles bcrypt's 72-byte limit by truncating if necessary.

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hash string

        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = self._truncate_password(plain_password)
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False

    def get_password_hash(self, password: str) -> str:
        """
        Hash a password using bcrypt

        Automatically handles bcrypt's 72-byte limit by truncating if necessary.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash string
        """
        password_bytes = self._truncate_password(password)
        salt = bcrypt.gensalt()
        hash_bytes = bcrypt.hashpw(password_bytes, salt)
        return hash_bytes.decode('utf-8')

    def _user_to_dict(self, user: DBUser, include_password: bool = False) -> Dict[str, Any]:
        """Convert User model to dict"""
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "disabled": user.disabled,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        if include_password:
            user_dict["hashed_password"] = user.hashed_password
        return user_dict

    async def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        user = await self.repository.get_by_username(username)
        if user:
            user_dict = self._user_to_dict(user, include_password=True)
            return UserInDB(**user_dict)
        return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user = await self.repository.get_by_id(user_id)
        if user:
            user_dict = self._user_to_dict(user)
            return User(**user_dict)
        return None

    async def create_user(self, username: str, password: str, email: Optional[str] = None,
                   full_name: Optional[str] = None) -> User:
        """
        Create a new user

        Args:
            username: Username
            password: Plain text password
            email: Optional email
            full_name: Optional full name

        Returns:
            User object

        Raises:
            ValueError: If user already exists
        """
        # Check if user exists
        existing_user = await self.repository.get_by_username(username)
        if existing_user:
            raise ValueError(f"User '{username}' already exists")

        # Check if email exists
        if email:
            existing_email = await self.repository.get_by_email(email)
            if existing_email:
                raise ValueError(f"Email '{email}' already in use")

        # Create new user
        user = DBUser(
            username=username,
            email=email or f"{username}@example.com",  # Email is required in DB
            full_name=full_name,
            hashed_password=self.get_password_hash(password),
            disabled=False,
            created_at=datetime.utcnow(),
            last_login=None
        )

        user = await self.repository.create(user)
        await self.session.commit()

        user_dict = self._user_to_dict(user)
        return User(**user_dict)

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.repository.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if user.disabled:
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        await self.repository.update(user)
        await self.session.commit()

        user_dict = self._user_to_dict(user, include_password=True)
        return UserInDB(**user_dict)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.jwt_access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """
        Create JWT refresh token

        Args:
            data: Data to encode in token

        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")

        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            username: str = payload.get("sub")
            exp: datetime = datetime.fromtimestamp(payload.get("exp"))
            token_type_in_payload: str = payload.get("type")

            if username is None:
                return None
            if token_type_in_payload != token_type:
                return None

            return TokenData(username=username, exp=exp)

        except JWTError:
            return None

    async def list_users(self) -> list[User]:
        """List all users"""
        users = await self.repository.list_all()
        return [
            User(**self._user_to_dict(user))
            for user in users
        ]

    async def delete_user(self, username: str) -> bool:
        """
        Delete a user

        Args:
            username: Username to delete

        Returns:
            True if deleted, False if user not found
        """
        user = await self.repository.get_by_username(username)
        if user:
            await self.repository.delete(user)
            await self.session.commit()
            return True
        return False

    async def update_user(self, username: str, **kwargs) -> Optional[User]:
        """
        Update user information

        Args:
            username: Username
            **kwargs: Fields to update (email, full_name, disabled)

        Returns:
            Updated User object or None if user not found
        """
        user = await self.repository.get_by_username(username)
        if not user:
            return None

        # Only allow updating specific fields
        allowed_fields = {"email", "full_name", "disabled"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)

        await self.repository.update(user)
        await self.session.commit()

        user_dict = self._user_to_dict(user)
        return User(**user_dict)
