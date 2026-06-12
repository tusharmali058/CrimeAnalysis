"""Accused service — business logic."""

from __future__ import annotations

import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.accused.models import Accused
from app.accused.repository import (
    create_accused,
    get_accused_by_accused_id,
    get_accused_by_id,
    get_top_offenders,
    list_accused,
)
from app.accused.schemas import AccusedCreate, AccusedListResponse, AccusedResponse


async def get_accused(db: AsyncSession, accused_db_id: int) -> AccusedResponse:
    accused = await get_accused_by_id(db, accused_db_id)
    if accused is None:
        raise ValueError(f"Accused with id {accused_db_id} not found")
    return AccusedResponse.model_validate(accused)


async def search_accused(
    db: AsyncSession,
    district: str | None = None,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> AccusedListResponse:
    items, total = await list_accused(db, district, status, category, search, page, page_size)
    return AccusedListResponse(
        items=[AccusedResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


async def create_new_accused(db: AsyncSession, data: AccusedCreate) -> AccusedResponse:
    existing = await get_accused_by_accused_id(db, data.accused_id)
    if existing:
        raise ValueError(f"Accused {data.accused_id} already exists")

    accused = Accused(**data.model_dump())
    accused = await create_accused(db, accused)
    return AccusedResponse.model_validate(accused)
