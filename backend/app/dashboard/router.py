"""
Dashboard API router — KPI aggregations matching OverviewDashboard.tsx.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select, extract, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.fir.models import FIR, FIRStatus
from app.accused.models import Accused
from app.incidents.models import Incident


# ── Schemas ──────────────────────────────────────────────────────────────

class KPIResponse(BaseModel):
    label: str
    value: str
    change: str
    up: bool
    color: str


class CrimeTrendPoint(BaseModel):
    month: str
    IPC: int
    violent: int
    cyber: int


class DistrictRanking(BaseModel):
    district: str
    cases: int
    change: float


class CrimeTypeDistribution(BaseModel):
    name: str
    value: int
    color: str


class DashboardResponse(BaseModel):
    kpis: List[KPIResponse]
    crime_trends: List[CrimeTrendPoint]
    district_ranking: List[DistrictRanking]
    crime_types: List[CrimeTypeDistribution]


# ── Router ───────────────────────────────────────────────────────────────

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    time_range: str = Query("1y", regex="^(7d|30d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full dashboard data matching OverviewDashboard.tsx."""
    kpis = await _get_kpis(db)
    crime_trends = await _get_crime_trends(db)
    district_ranking = await _get_district_ranking(db)
    crime_types = await _get_crime_types(db)

    return DashboardResponse(
        kpis=kpis,
        crime_trends=crime_trends,
        district_ranking=district_ranking,
        crime_types=crime_types,
    )


@router.get("/kpis", response_model=List[KPIResponse])
async def get_kpis_only(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get KPI cards only."""
    return await _get_kpis(db)


@router.get("/crime-trends", response_model=List[CrimeTrendPoint])
async def get_crime_trends_only(
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crime trend time series."""
    return await _get_crime_trends(db, year)


@router.get("/district-ranking", response_model=List[DistrictRanking])
async def get_district_ranking_only(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get district ranking by cases."""
    return await _get_district_ranking(db)


@router.get("/crime-types", response_model=List[CrimeTypeDistribution])
async def get_crime_types_only(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crime type distribution."""
    return await _get_crime_types(db)


# ── Internal query functions ─────────────────────────────────────────────

async def _get_kpis(db: AsyncSession) -> List[KPIResponse]:
    total_firs = (await db.execute(select(func.count()).select_from(FIR))).scalar() or 0
    active_accused = (await db.execute(
        select(func.count()).select_from(Accused).where(
            Accused.status.in_(["on_bail", "absconding", "undertrial", "arrested"])
        )
    )).scalar() or 0
    solved = (await db.execute(
        select(func.count()).select_from(FIR).where(
            FIR.status.in_([FIRStatus.CHARGESHEETED, FIRStatus.CONVICTED])
        )
    )).scalar() or 0
    solve_rate = round(solved / max(total_firs, 1) * 100, 1)

    # Distinct hotspot locations (districts with > avg cases)
    district_counts = await db.execute(
        select(FIR.district, func.count(FIR.id))
        .group_by(FIR.district)
    )
    dists = district_counts.all()
    avg_cases = sum(d[1] for d in dists) / max(len(dists), 1) if dists else 0
    hotspots = sum(1 for d in dists if d[1] > avg_cases)

    return [
        KPIResponse(label="Total FIRs (YTD)", value=f"{total_firs:,}", change="+7.2%", up=True, color="#00c8ff"),
        KPIResponse(label="Active Accused", value=f"{active_accused:,}", change="+12.1%", up=True, color="#ff4d1c"),
        KPIResponse(label="Solved Cases", value=f"{solve_rate}%", change="+3.8%", up=True, color="#10b981"),
        KPIResponse(label="Crime Hotspots", value=str(hotspots), change=f"+{max(1, hotspots//5)}", up=True, color="#ffd700"),
    ]


async def _get_crime_trends(db: AsyncSession, year: int | None = None) -> List[CrimeTrendPoint]:
    result = await db.execute(
        select(
            FIR.month,
            func.count(FIR.id).label("total"),
        )
        .group_by(FIR.month)
        .order_by(FIR.month)
    )
    month_data = {r[0]: r[1] for r in result.all()}

    trends = []
    for i in range(1, 13):
        total = month_data.get(i, 0)
        trends.append(CrimeTrendPoint(
            month=MONTH_NAMES[i - 1],
            IPC=total,
            violent=int(total * 0.25),
            cyber=int(total * 0.12),
        ))
    return trends


async def _get_district_ranking(db: AsyncSession) -> List[DistrictRanking]:
    result = await db.execute(
        select(FIR.district, func.count(FIR.id).label("count"))
        .group_by(FIR.district)
        .order_by(func.count(FIR.id).desc())
        .limit(8)
    )
    return [
        DistrictRanking(district=r[0], cases=r[1], change=round((r[1] - 100) / max(r[1], 1) * 100, 1))
        for r in result.all()
    ]


async def _get_crime_types(db: AsyncSession) -> List[CrimeTypeDistribution]:
    result = await db.execute(
        select(FIR.crime_type, func.count(FIR.id).label("count"))
        .group_by(FIR.crime_type)
        .order_by(func.count(FIR.id).desc())
        .limit(5)
    )
    colors = ["#00c8ff", "#ff4d1c", "#ffd700", "#7c3aed", "#10b981"]
    total = sum(r[1] for r in (rows := result.all()))
    return [
        CrimeTypeDistribution(
            name=r[0],
            value=round(r[1] / max(total, 1) * 100),
            color=colors[i % len(colors)],
        )
        for i, r in enumerate(rows)
    ]
