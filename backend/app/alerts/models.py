"""
Alert model and router — matches App.tsx AlertsView data shape.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import DateTime, Enum, String, Text, Boolean, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.base import Base
from app.db.session import get_db


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    SPIKE = "SPIKE"
    GANG = "GANG"
    REPEAT = "REPEAT"
    HOTSPOT = "HOTSPOT"
    FINANCIAL = "FINANCIAL"
    FORECAST = "FORECAST"
    ANOMALY = "ANOMALY"


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType, name="alert_type"), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    crime: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, name="alert_severity"), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Schemas ──────────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    """Matches App.tsx alert data shape."""
    id: str
    type: str
    district: str
    crime: str
    detail: str
    severity: str
    time: str
    is_read: bool = False

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    unread: int


# ── Router ───────────────────────────────────────────────────────────────

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def get_alerts(
    severity: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get alerts matching App.tsx AlertsView shape."""
    query = select(Alert).order_by(desc(Alert.created_at))
    if severity:
        query = query.where(Alert.severity == severity)
    if unread_only:
        query = query.where(Alert.is_read == False)
    query = query.limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    unread_count = (await db.execute(
        select(func.count()).select_from(Alert).where(Alert.is_read == False)
    )).scalar() or 0

    total = (await db.execute(
        select(func.count()).select_from(Alert)
    )).scalar() or 0

    return AlertListResponse(
        alerts=[
            AlertResponse(
                id=a.alert_id,
                type=a.alert_type.value,
                district=a.district,
                crime=a.crime,
                detail=a.detail,
                severity=a.severity.value,
                time=_time_ago(a.created_at),
                is_read=a.is_read,
            )
            for a in alerts
        ],
        total=total,
        unread=unread_count,
    )


@router.post("/{alert_id}/review")
async def review_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as reviewed."""
    result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    alert.reviewed_by = current_user.username
    alert.reviewed_at = datetime.utcnow()
    db.add(alert)
    return {"status": "reviewed", "alert_id": alert_id}


def _time_ago(dt: datetime) -> str:
    """Convert datetime to '14m ago' style string."""
    from datetime import timezone
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        from datetime import timezone as tz
        dt = dt.replace(tzinfo=tz.utc)
    diff = now - dt
    minutes = int(diff.total_seconds() / 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"
