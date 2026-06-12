"""Victims service and router."""

from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.victims.models import Victim
from app.victims.repository import list_victims, create_victim
from app.victims.schemas import VictimCreate, VictimListResponse, VictimResponse

router = APIRouter(prefix="/victims", tags=["Victims"])


@router.get("", response_model=VictimListResponse)
async def list_victims_route(
    fir_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await list_victims(db, fir_id, page, page_size)
    return VictimListResponse(
        items=[VictimResponse.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=VictimResponse, status_code=201)
async def create_victim_route(
    data: VictimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    victim = Victim(**data.model_dump())
    victim = await create_victim(db, victim)
    return VictimResponse.model_validate(victim)
