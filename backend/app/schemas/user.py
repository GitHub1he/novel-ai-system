from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone: Optional[str] = None
    preferred_genre: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    preferred_genre: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_admin: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
