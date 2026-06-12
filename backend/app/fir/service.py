"""
FIR service — business logic layer.
"""

from __future__ import annotations

import math
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.fir.models import FIR
from app.fir.repository import (
    create_fir,
    get_fir_by_id,
    get_fir_by_number,
    list_firs,
    update_fir,
)
from app.fir.schemas import FIRCreate, FIRFilter, FIRListResponse, FIRResponse, FIRUpdate


async def get_fir(db: AsyncSession, fir_id: int) -> FIRResponse:
    fir = await get_fir_by_id(db, fir_id)
    if fir is None:
        raise ValueError(f"FIR with id {fir_id} not found")
    return FIRResponse.model_validate(fir)


async def search_firs(
    db: AsyncSession,
    filters: FIRFilter | None = None,
    page: int = 1,
    page_size: int = 20,
) -> FIRListResponse:
    items, total = await list_firs(db, filters, page, page_size)
    return FIRListResponse(
        items=[FIRResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


async def create_new_fir(db: AsyncSession, data: FIRCreate) -> FIRResponse:
    # Check for duplicate
    existing = await get_fir_by_number(db, data.fir_number)
    if existing:
        raise ValueError(f"FIR {data.fir_number} already exists")

    fir = FIR(**data.model_dump())
    # Compute derived fields
    if fir.date_filed:
        fir.day_of_week = fir.date_filed.strftime("%A")
        fir.month = fir.date_filed.month
        fir.year = fir.date_filed.year

    fir = await create_fir(db, fir)
    return FIRResponse.model_validate(fir)


async def update_existing_fir(
    db: AsyncSession, fir_id: int, data: FIRUpdate
) -> FIRResponse:
    fir = await get_fir_by_id(db, fir_id)
    if fir is None:
        raise ValueError(f"FIR with id {fir_id} not found")

    fir = await update_fir(db, fir, data.model_dump(exclude_unset=True))
    return FIRResponse.model_validate(fir)
