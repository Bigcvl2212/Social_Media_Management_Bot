"""
Pydantic schemas for API request/response models
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user API responses"""
    id: int
    is_active: bool
    is_verified: bool
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None