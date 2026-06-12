"""
Accused ORM model — matches the OffenderProfiling frontend component.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import Date, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AccusedStatus(str, enum.Enum):
    ON_BAIL = "on_bail"
    ABSCONDING = "absconding"
    CONVICTED = "convicted"
    UNDERTRIAL = "undertrial"
    ARRESTED = "arrested"
    RELEASED = "released"


class Accused(Base):
    """Accused / suspect record linked to FIRs."""

    __tablename__ = "accused"

    accused_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    aliases: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # ["alias1", "alias2"]
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    police_station: Mapped[str | None] = mapped_column(String(150), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[AccusedStatus] = mapped_column(
        Enum(AccusedStatus, name="accused_status"),
        default=AccusedStatus.UNDERTRIAL,
        index=True,
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Cyber, Violent, etc.
    risk_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    last_known_location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    first_offence_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    modus_operandi: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Criminological profile scores — maps to OffenderProfiling radar chart
    profile_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Expected: {"aggression": 0-100, "sophistication": 0-100, "recidivism": 0-100,
    #            "network": 0-100, "mobility": 0-100, "financial": 0-100}

    # Incident timeline data
    incident_timeline: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Expected: [{"year": "2019", "incidents": 1}, ...]

    # Known associates (accused_ids)
    associate_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # FK to FIR (primary FIR)
    fir_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("firs.id"), nullable=True
    )
    fir = relationship("FIR", back_populates="accused")

    # Total incident count (denormalized for performance)
    incident_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Accused {self.accused_id} [{self.name}] risk={self.risk_score}>"
