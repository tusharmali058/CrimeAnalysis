"""
FIR (First Information Report) ORM model.
"""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, Float, Integer, JSON, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FIRStatus(str, enum.Enum):
    REGISTERED = "registered"
    UNDER_INVESTIGATION = "under_investigation"
    CHARGESHEETED = "chargesheeted"
    CLOSED = "closed"
    CONVICTED = "convicted"
    ACQUITTED = "acquitted"


class CrimeSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FIR(Base):
    """First Information Report — the core crime record."""

    __tablename__ = "firs"

    fir_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    police_station: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    date_filed: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    date_of_offence: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Crime classification
    crime_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    crime_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ipc_sections: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # ["302", "34"]
    act_sections: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brief_facts: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[FIRStatus] = mapped_column(
        Enum(FIRStatus, name="fir_status"),
        default=FIRStatus.REGISTERED,
        index=True,
        nullable=False,
    )
    severity: Mapped[CrimeSeverity] = mapped_column(
        Enum(CrimeSeverity, name="crime_severity"),
        default=CrimeSeverity.MEDIUM,
        nullable=False,
    )

    # Complainant
    complainant_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    complainant_contact: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Location
    location_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    geo_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Investigation
    investigating_officer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    io_contact: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Time metadata
    time_of_offence: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "HH:MM"
    day_of_week: Mapped[str | None] = mapped_column(String(10), nullable=True)
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    # Relationships
    accused = relationship("Accused", back_populates="fir", lazy="selectin")
    victims = relationship("Victim", back_populates="fir", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FIR {self.fir_number} [{self.crime_type}] {self.district}>"
