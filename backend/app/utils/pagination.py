"""
Pagination utilities.
"""

from __future__ import annotations

import math
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    """Create a standard pagination envelope."""
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total > 0 else 0,
        "has_next": page * page_size < total,
        "has_prev": page > 1,
    }
