"""
FIR request/response schemas.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.fir.models import CrimeSeverity, FIRStatus


class FIRCreate(BaseModel):
    fir_number: str
    district: str
    police_station: str
    date_filed: date
    date_of_offence: Optional[date] = None
    crime_type: str
    crime_category: Optional[str] = None
    ipc_sections: Optional[List[str]] = None
    act_sections: Optional[List[str]] = None
    description: Optional[str] = None
    brief_facts: Optional[str] = None
    status: FIRStatus = FIRStatus.REGISTERED
    severity: CrimeSeverity = CrimeSeverity.MEDIUM
    complainant_name: Optional[str] = None
    complainant_contact: Optional[str] = None
    location_name: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    investigating_officer: Optional[str] = None
    time_of_offence: Optional[str] = None


class FIRUpdate(BaseModel):
    status: Optional[FIRStatus] = None
    severity: Optional[CrimeSeverity] = None
    description: Optional[str] = None
    investigating_officer: Optional[str] = None
    brief_facts: Optional[str] = None


class FIRResponse(BaseModel):
    id: int
    fir_number: str
    district: str
    police_station: str
    date_filed: date
    date_of_offence: Optional[date] = None
    crime_type: str
    crime_category: Optional[str] = None
    ipc_sections: Optional[List[str]] = None
    description: Optional[str] = None
    status: FIRStatus
    severity: CrimeSeverity
    complainant_name: Optional[str] = None
    location_name: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    investigating_officer: Optional[str] = None
    time_of_offence: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FIRListResponse(BaseModel):
    items: List[FIRResponse]
    total: int
    page: int
    page_size: int
    pages: int


class FIRFilter(BaseModel):
    district: Optional[str] = None
    police_station: Optional[str] = None
    crime_type: Optional[str] = None
    status: Optional[FIRStatus] = None
    severity: Optional[CrimeSeverity] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    year: Optional[int] = None
    search: Optional[str] = None
