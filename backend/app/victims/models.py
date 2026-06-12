"""
Victim ORM model.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Victim(Base):
    __tablename__ = "victims"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    injury_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    loss_amount: Mapped[float | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    fir_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("firs.id"), nullable=True
    )
    fir = relationship("FIR", back_populates="victims")

    def __repr__(self) -> str:
        return f"<Victim {self.name}>"
