"""
FIR repository — database queries.
"""

from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.fir.models import FIR
from app.fir.schemas import FIRFilter


async def get_fir_by_id(db: AsyncSession, fir_id: int) -> FIR | None:
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    return result.scalar_one_or_none()


async def get_fir_by_number(db: AsyncSession, fir_number: str) -> FIR | None:
    result = await db.execute(select(FIR).where(FIR.fir_number == fir_number))
    return result.scalar_one_or_none()


async def list_firs(
    db: AsyncSession,
    filters: FIRFilter | None = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[list[FIR], int]:
    """List FIRs with filtering and pagination."""
    query = select(FIR)
    count_query = select(func.count()).select_from(FIR)

    if filters:
        conditions = []
        if filters.district:
            conditions.append(FIR.district.ilike(f"%{filters.district}%"))
        if filters.police_station:
            conditions.append(FIR.police_station.ilike(f"%{filters.police_station}%"))
        if filters.crime_type:
            conditions.append(FIR.crime_type.ilike(f"%{filters.crime_type}%"))
        if filters.status:
            conditions.append(FIR.status == filters.status)
        if filters.severity:
            conditions.append(FIR.severity == filters.severity)
        if filters.date_from:
            conditions.append(FIR.date_filed >= filters.date_from)
        if filters.date_to:
            conditions.append(FIR.date_filed <= filters.date_to)
        if filters.year:
            conditions.append(FIR.year == filters.year)
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    FIR.fir_number.ilike(search_term),
                    FIR.description.ilike(search_term),
                    FIR.complainant_name.ilike(search_term),
                    FIR.location_name.ilike(search_term),
                )
            )

        if conditions:
            combined = and_(*conditions)
            query = query.where(combined)
            count_query = count_query.where(combined)

    # Total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(FIR.date_filed.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return items, total


async def create_fir(db: AsyncSession, fir: FIR) -> FIR:
    db.add(fir)
    await db.flush()
    await db.refresh(fir)
    return fir


async def update_fir(db: AsyncSession, fir: FIR, data: dict) -> FIR:
    for field, value in data.items():
        if hasattr(fir, field) and value is not None:
            setattr(fir, field, value)
    db.add(fir)
    await db.flush()
    await db.refresh(fir)
    return fir


async def get_fir_count_by_district(db: AsyncSession) -> list[dict]:
    """Aggregate FIR counts by district."""
    result = await db.execute(
        select(FIR.district, func.count(FIR.id).label("count"))
        .group_by(FIR.district)
        .order_by(func.count(FIR.id).desc())
    )
    return [{"district": row[0], "count": row[1]} for row in result.all()]


async def get_fir_count_by_crime_type(db: AsyncSession) -> list[dict]:
    """Aggregate FIR counts by crime type."""
    result = await db.execute(
        select(FIR.crime_type, func.count(FIR.id).label("count"))
        .group_by(FIR.crime_type)
        .order_by(func.count(FIR.id).desc())
    )
    return [{"crime_type": row[0], "count": row[1]} for row in result.all()]


async def get_monthly_trend(db: AsyncSession, year: int | None = None) -> list[dict]:
    """Monthly FIR filing trend."""
    query = (
        select(FIR.month, func.count(FIR.id).label("count"))
        .group_by(FIR.month)
        .order_by(FIR.month)
    )
    if year:
        query = query.where(FIR.year == year)
    result = await db.execute(query)
    return [{"month": row[0], "count": row[1]} for row in result.all()]
