"""Incidents schemas and router."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.incidents.models import Incident


class IncidentResponse(BaseModel):
    id: int
    district: str
    crime_type: str
    severity: str
    incident_time: datetime
    location_name: Optional[str] = None
    hour_of_day: Optional[int] = None
    day_of_week: Optional[str] = None

    class Config:
        from_attributes = True


class LiveIncidentResponse(BaseModel):
    """Matches CrimeMap.tsx recentIncidents shape."""
    time: str
    district: str
    type: str
    severity: str


router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("/live", response_model=List[LiveIncidentResponse])
async def get_live_incidents(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get most recent incidents for live feed."""
    result = await db.execute(
        select(Incident)
        .order_by(desc(Incident.incident_time))
        .limit(limit)
    )
    incidents = result.scalars().all()
    return [
        LiveIncidentResponse(
            time=inc.incident_time.strftime("%H:%M"),
            district=inc.district,
            type=inc.crime_type,
            severity=inc.severity,
        )
        for inc in incidents
    ]


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    district: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Incident)
    if district:
        query = query.where(Incident.district.ilike(f"%{district}%"))
    if crime_type:
        query = query.where(Incident.crime_type.ilike(f"%{crime_type}%"))
    query = query.order_by(desc(Incident.incident_time))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [IncidentResponse.model_validate(i) for i in result.scalars().all()]
