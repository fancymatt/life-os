"""Authentication Service

Handles user authentication, password hashing, and JWT token management.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

from jose import JWTError, jwt
from passlib.context import CryptContext

from api.config import settings
from api.models.auth import UserInDB, TokenData, User


class AuthService:
    """Service for authentication and authorization"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Store users in persistent data directory
        data_dir = settings.base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = data_dir / "users.json"
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Ensure users file exists"""
        if not self.users_file.exists():
            self.users_file.write_text(json.dumps({}, indent=2))

    def _load_users(self) -> Dict[str, dict]:
        """Load users from file"""
        try:
            return json.loads(self.users_file.read_text())
        except:
            return {}

    def _save_users(self, users: Dict[str, dict]):
        """Save users to file"""
        self.users_file.write_text(json.dumps(users, indent=2, default=str))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        users = self._load_users()
        user_data = users.get(username)
        if user_data:
            return UserInDB(**user_data)
        return None

    def create_user(self, username: str, password: str, email: Optional[str] = None,
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
        users = self._load_users()

        if username in users:
            raise ValueError(f"User '{username}' already exists")

        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "hashed_password": self.get_password_hash(password),
            "disabled": False,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }

        users[username] = user_data
        self._save_users(users)

        return User(**{k: v for k, v in user_data.items() if k != "hashed_password"})

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if user.disabled:
            return None

        # Update last login
        users = self._load_users()
        users[username]["last_login"] = datetime.now().isoformat()
        self._save_users(users)

        return user

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

    def list_users(self) -> list[User]:
        """List all users"""
        users = self._load_users()
        return [
            User(**{k: v for k, v in user_data.items() if k != "hashed_password"})
            for user_data in users.values()
        ]

    def delete_user(self, username: str) -> bool:
        """
        Delete a user

        Args:
            username: Username to delete

        Returns:
            True if deleted, False if user not found
        """
        users = self._load_users()
        if username in users:
            del users[username]
            self._save_users(users)
            return True
        return False

    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """
        Update user information

        Args:
            username: Username
            **kwargs: Fields to update (email, full_name, disabled)

        Returns:
            Updated User object or None if user not found
        """
        users = self._load_users()
        if username not in users:
            return None

        # Only allow updating specific fields
        allowed_fields = {"email", "full_name", "disabled"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                users[username][key] = value

        self._save_users(users)
        return User(**{k: v for k, v in users[username].items() if k != "hashed_password"})


# Global singleton
auth_service = AuthService()
