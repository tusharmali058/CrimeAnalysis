"""Victims schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class VictimCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    injury_type: Optional[str] = None
    loss_amount: Optional[float] = None
    description: Optional[str] = None
    fir_id: Optional[int] = None


class VictimResponse(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    district: Optional[str] = None
    injury_type: Optional[str] = None
    loss_amount: Optional[float] = None
    fir_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VictimListResponse(BaseModel):
    items: List[VictimResponse]
    total: int
    page: int
    page_size: int
