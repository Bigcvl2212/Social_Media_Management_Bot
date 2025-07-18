"""
User service for user management operations
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def authenticate(self, email_or_username: str, password: str) -> Optional[User]:
        """Authenticate user with email/username and password"""
        # Try to find user by email first, then username
        user = await self.get_by_email(email_or_username)
        if not user:
            user = await self.get_by_username(email_or_username)
        
        if not user or not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = func.now()
            await self.db.commit()
    
    async def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def activate(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        return user