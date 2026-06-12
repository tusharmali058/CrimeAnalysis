"""
FIR API router.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.fir.schemas import (
    FIRCreate,
    FIRFilter,
    FIRListResponse,
    FIRResponse,
    FIRUpdate,
)
from app.fir.service import create_new_fir, get_fir, search_firs, update_existing_fir

router = APIRouter(prefix="/fir", tags=["FIR"])


@router.get("", response_model=FIRListResponse)
async def list_fir_records(
    district: Optional[str] = Query(None),
    police_station: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List FIRs with filtering and pagination."""
    filters = FIRFilter(
        district=district,
        police_station=police_station,
        crime_type=crime_type,
        search=search,
        year=year,
    )
    return await search_firs(db, filters, page, page_size)


@router.get("/{fir_id}", response_model=FIRResponse)
async def get_fir_by_id_route(
    fir_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific FIR by ID."""
    try:
        return await get_fir(db, fir_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=FIRResponse, status_code=201)
async def create_fir_route(
    data: FIRCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new FIR."""
    try:
        return await create_new_fir(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{fir_id}", response_model=FIRResponse)
async def update_fir_route(
    fir_id: int,
    data: FIRUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing FIR."""
    try:
        return await update_existing_fir(db, fir_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
