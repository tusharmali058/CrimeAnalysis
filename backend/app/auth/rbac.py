"""
Role-based access control (RBAC) dependencies for FastAPI.
"""

from __future__ import annotations

from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole
from app.auth.service import decode_token, get_user_by_id
from app.db.session import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency — extract and validate the current user from JWT."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    return user


def require_role(*roles: UserRole):
    """
    Dependency factory — require the user to have one of the specified roles.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMINISTRATOR))])
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' does not have access. Required: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


# ── Pre-built role dependencies ──────────────────────────────────────────

require_admin = require_role(UserRole.ADMINISTRATOR)
require_supervisor = require_role(UserRole.SUPERVISOR, UserRole.ADMINISTRATOR)
require_analyst = require_role(UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMINISTRATOR)
require_investigator = require_role(
    UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMINISTRATOR
)
require_any_role = require_role(
    UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR,
    UserRole.ADMINISTRATOR, UserRole.POLICYMAKER,
)
