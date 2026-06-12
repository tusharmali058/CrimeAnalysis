"""Victims repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.victims.models import Victim


async def list_victims(db: AsyncSession, fir_id: int | None = None, page: int = 1, page_size: int = 20):
    query = select(Victim)
    count_query = select(func.count()).select_from(Victim)
    if fir_id:
        query = query.where(Victim.fir_id == fir_id)
        count_query = count_query.where(Victim.fir_id == fir_id)
    total = (await db.execute(count_query)).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_victim(db: AsyncSession, victim: Victim) -> Victim:
    db.add(victim)
    await db.flush()
    await db.refresh(victim)
    return victim
