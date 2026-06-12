"""
Auth request/response schemas (Pydantic models).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.auth.models import UserRole


# ── Request Schemas ──────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., min_length=2, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.ANALYST
    badge_number: Optional[str] = None
    department: Optional[str] = None
    district: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


# ── Response Schemas ─────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    badge_number: Optional[str] = None
    department: Optional[str] = None
    district: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    district: Optional[str] = None
