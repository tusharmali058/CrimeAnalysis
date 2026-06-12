"""
Accused schemas — matches OffenderProfiling.tsx data structures.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.accused.models import AccusedStatus


class AccusedCreate(BaseModel):
    accused_id: str
    name: str
    aliases: Optional[List[str]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    district: str
    police_station: Optional[str] = None
    address: Optional[str] = None
    status: AccusedStatus = AccusedStatus.UNDERTRIAL
    category: Optional[str] = None
    risk_score: float = 50.0
    last_known_location: Optional[str] = None
    first_offence_date: Optional[date] = None
    modus_operandi: Optional[str] = None
    profile_scores: Optional[Dict[str, int]] = None
    incident_timeline: Optional[List[Dict[str, Any]]] = None
    associate_ids: Optional[List[str]] = None
    fir_id: Optional[int] = None
    incident_count: int = 0


class AccusedUpdate(BaseModel):
    status: Optional[AccusedStatus] = None
    risk_score: Optional[float] = None
    last_known_location: Optional[str] = None
    modus_operandi: Optional[str] = None
    profile_scores: Optional[Dict[str, int]] = None


class AccusedResponse(BaseModel):
    """Matches the offender object shape in OffenderProfiling.tsx."""
    id: int
    accused_id: str
    name: str
    aliases: Optional[List[str]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    district: str
    police_station: Optional[str] = None
    status: AccusedStatus
    category: Optional[str] = None
    risk_score: float
    last_known_location: Optional[str] = None
    first_offence_date: Optional[date] = None
    modus_operandi: Optional[str] = None
    profile_scores: Optional[Dict[str, int]] = None
    incident_timeline: Optional[List[Dict[str, Any]]] = None
    associate_ids: Optional[List[str]] = None
    incident_count: int
    created_at: datetime

    class Config:
        from_attributes = True

    @property
    def status_display(self) -> str:
        """Human-readable status for frontend."""
        mapping = {
            AccusedStatus.ON_BAIL: "On Bail",
            AccusedStatus.ABSCONDING: "Absconding",
            AccusedStatus.CONVICTED: "Convicted",
            AccusedStatus.UNDERTRIAL: "Undertrial",
            AccusedStatus.ARRESTED: "Arrested",
            AccusedStatus.RELEASED: "Released",
        }
        return mapping.get(self.status, self.status.value)


class AccusedListResponse(BaseModel):
    items: List[AccusedResponse]
    total: int
    page: int
    page_size: int
    pages: int
