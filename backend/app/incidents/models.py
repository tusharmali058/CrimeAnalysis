"""
Crime Incident model — time-stamped individual crime events.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    fir_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("firs.id"), nullable=True)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    police_station: Mapped[str | None] = mapped_column(String(150), nullable=True)
    crime_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    geo_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    hour_of_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[str | None] = mapped_column(String(10), nullable=True)

    def __repr__(self) -> str:
        return f"<Incident {self.crime_type} @ {self.district}>"
