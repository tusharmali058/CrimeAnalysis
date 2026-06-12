"""Accused API router."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.accused.schemas import AccusedCreate, AccusedListResponse, AccusedResponse
from app.accused.service import create_new_accused, get_accused, search_accused

router = APIRouter(prefix="/accused", tags=["Accused"])


@router.get("", response_model=AccusedListResponse)
async def list_accused_route(
    district: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List accused with filtering and pagination."""
    return await search_accused(db, district, status, category, search, page, page_size)


@router.get("/{accused_id}", response_model=AccusedResponse)
async def get_accused_route(
    accused_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get accused by database ID."""
    try:
        return await get_accused(db, accused_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=AccusedResponse, status_code=201)
async def create_accused_route(
    data: AccusedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new accused record."""
    try:
        return await create_new_accused(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
