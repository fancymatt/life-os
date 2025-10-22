"""
User Repository

Data access layer for User entity operations.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import User


class UserRepository:
    """Repository for User database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[User]:
        """Get all users"""
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        """Create a new user"""
        self.session.add(user)
        await self.session.flush()  # Get ID without committing
        return user

    async def update(self, user: User) -> User:
        """Update user"""
        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        """Delete user"""
        await self.session.delete(user)
        await self.session.flush()
