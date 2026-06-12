"""
FastAPI dependency injection providers.
"""

from __future__ import annotations

from app.config import get_settings, Settings
from app.db.session import get_db


__all__ = ["get_settings", "get_db"]
