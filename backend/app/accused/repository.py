"""
Accused repository — database queries.
"""

from __future__ import annotations

import math
from typing import Tuple

from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.accused.models import Accused


async def get_accused_by_id(db: AsyncSession, accused_db_id: int) -> Accused | None:
    result = await db.execute(select(Accused).where(Accused.id == accused_db_id))
    return result.scalar_one_or_none()


async def get_accused_by_accused_id(db: AsyncSession, accused_id: str) -> Accused | None:
    result = await db.execute(select(Accused).where(Accused.accused_id == accused_id))
    return result.scalar_one_or_none()


async def list_accused(
    db: AsyncSession,
    district: str | None = None,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[list[Accused], int]:
    query = select(Accused)
    count_query = select(func.count()).select_from(Accused)

    conditions = []
    if district:
        conditions.append(Accused.district.ilike(f"%{district}%"))
    if status:
        conditions.append(Accused.status == status)
    if category:
        conditions.append(Accused.category.ilike(f"%{category}%"))
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Accused.name.ilike(search_term),
                Accused.accused_id.ilike(search_term),
            )
        )

    if conditions:
        combined = and_(*conditions)
        query = query.where(combined)
        count_query = count_query.where(combined)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Accused.risk_score.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = list(result.scalars().all())
    return items, total


async def create_accused(db: AsyncSession, accused: Accused) -> Accused:
    db.add(accused)
    await db.flush()
    await db.refresh(accused)
    return accused


async def get_top_offenders(db: AsyncSession, limit: int = 10) -> list[Accused]:
    """Get top offenders by risk score."""
    result = await db.execute(
        select(Accused)
        .order_by(Accused.risk_score.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_accused_count_by_status(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Accused.status, func.count(Accused.id).label("count"))
        .group_by(Accused.status)
    )
    return [{"status": row[0], "count": row[1]} for row in result.all()]
