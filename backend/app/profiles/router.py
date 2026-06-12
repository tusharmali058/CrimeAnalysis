"""
Profiles API router — offender profiling matching OffenderProfiling.tsx.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.accused.models import Accused
from app.accused.schemas import AccusedResponse
from app.profiles.scoring import compute_risk_score


# ── Schemas matching OffenderProfiling.tsx ────────────────────────────────

class ProfileRadarData(BaseModel):
    subject: str
    value: int


class OffenderProfileResponse(BaseModel):
    """Full offender profile matching OffenderProfiling.tsx shape."""
    id: str
    name: str
    alias: List[str]
    age: Optional[int]
    gender: Optional[str]
    district: str
    ps: Optional[str]
    incidents: int
    status: str
    category: Optional[str]
    riskScore: float
    lastKnown: Optional[str]
    firstOffence: Optional[str]
    modus: Optional[str]
    associates: List[str]
    profile: Dict[str, int]
    timeline: List[Dict[str, Any]]


class RiskAssessmentResponse(BaseModel):
    accused_id: str
    risk_score: float
    risk_level: str
    feature_importance: Dict[str, float]
    profile_scores: Dict[str, int]
    explanation: List[str]


# ── Router ───────────────────────────────────────────────────────────────

router = APIRouter(prefix="/profiles", tags=["Offender Profiling"])


@router.get("/list", response_model=List[OffenderProfileResponse])
async def list_offender_profiles(
    district: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_risk: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List offender profiles matching OffenderProfiling.tsx sidebar."""
    query = select(Accused)
    if district:
        query = query.where(Accused.district.ilike(f"%{district}%"))
    if category:
        query = query.where(Accused.category.ilike(f"%{category}%"))
    if min_risk:
        query = query.where(Accused.risk_score >= min_risk)
    if search:
        from sqlalchemy import or_
        query = query.where(or_(
            Accused.name.ilike(f"%{search}%"),
            Accused.accused_id.ilike(f"%{search}%"),
        ))
    query = query.order_by(Accused.risk_score.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    accused_list = result.scalars().all()

    return [_to_profile_response(a) for a in accused_list]


@router.get("/{accused_id}", response_model=OffenderProfileResponse)
async def get_offender_profile(
    accused_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed offender profile by accused ID."""
    result = await db.execute(
        select(Accused).where(Accused.accused_id == accused_id)
    )
    accused = result.scalar_one_or_none()
    if not accused:
        raise HTTPException(status_code=404, detail=f"Accused {accused_id} not found")

    return _to_profile_response(accused)


@router.get("/{accused_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    accused_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute explainable risk assessment for an accused."""
    result = await db.execute(
        select(Accused).where(Accused.accused_id == accused_id)
    )
    accused = result.scalar_one_or_none()
    if not accused:
        raise HTTPException(status_code=404, detail=f"Accused {accused_id} not found")

    assessment = compute_risk_score(
        incident_count=accused.incident_count,
        districts_active=1,
        status=accused.status.value if accused.status else "undertrial",
        network_degree=len(accused.associate_ids) if accused.associate_ids else 0,
    )

    return RiskAssessmentResponse(
        accused_id=accused_id,
        risk_score=assessment["risk_score"],
        risk_level=assessment["risk_level"],
        feature_importance=assessment["feature_importance"],
        profile_scores=assessment["profile_scores"],
        explanation=assessment["explanation"],
    )


@router.get("/{accused_id}/timeline")
async def get_offender_timeline(
    accused_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get incident timeline for offender."""
    result = await db.execute(
        select(Accused).where(Accused.accused_id == accused_id)
    )
    accused = result.scalar_one_or_none()
    if not accused:
        raise HTTPException(status_code=404, detail=f"Accused {accused_id} not found")

    return {
        "accused_id": accused_id,
        "timeline": accused.incident_timeline or [],
    }


@router.get("/{accused_id}/associates")
async def get_offender_associates(
    accused_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get known associates for an offender."""
    result = await db.execute(
        select(Accused).where(Accused.accused_id == accused_id)
    )
    accused = result.scalar_one_or_none()
    if not accused:
        raise HTTPException(status_code=404, detail=f"Accused {accused_id} not found")

    associate_ids = accused.associate_ids or []
    associates = []
    if associate_ids:
        assoc_result = await db.execute(
            select(Accused).where(Accused.accused_id.in_(associate_ids))
        )
        for a in assoc_result.scalars().all():
            associates.append({
                "accused_id": a.accused_id,
                "name": a.name,
                "district": a.district,
                "status": a.status.value if a.status else "unknown",
                "risk_score": a.risk_score,
                "category": a.category,
            })

    return {"accused_id": accused_id, "associates": associates}


def _to_profile_response(accused: Accused) -> OffenderProfileResponse:
    """Convert Accused ORM model to OffenderProfiling.tsx shape."""
    status_map = {
        "on_bail": "On Bail",
        "absconding": "Absconding",
        "convicted": "Convicted",
        "undertrial": "Undertrial",
        "arrested": "Arrested",
        "released": "Released",
    }

    profile = accused.profile_scores or {
        "aggression": 50, "sophistication": 50, "recidivism": 50,
        "network": 50, "mobility": 50, "financial": 50,
    }

    return OffenderProfileResponse(
        id=accused.accused_id,
        name=accused.name,
        alias=accused.aliases if isinstance(accused.aliases, list) else [],
        age=accused.age,
        gender=accused.gender,
        district=accused.district,
        ps=accused.police_station,
        incidents=accused.incident_count,
        status=status_map.get(accused.status.value, accused.status.value) if accused.status else "Unknown",
        category=accused.category,
        riskScore=accused.risk_score,
        lastKnown=accused.last_known_location,
        firstOffence=str(accused.first_offence_date) if accused.first_offence_date else None,
        modus=accused.modus_operandi,
        associates=accused.associate_ids if isinstance(accused.associate_ids, list) else [],
        profile=profile,
        timeline=accused.incident_timeline if isinstance(accused.incident_timeline, list) else [],
    )
