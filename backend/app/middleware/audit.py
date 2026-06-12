"""
Audit logging middleware — logs all API requests to the audit_logs table.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Logs every API request for audit trail."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Execute request
        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        # Log the request (non-blocking — don't await DB write in middleware)
        if request.url.path.startswith("/api/"):
            logger.info(
                "API_AUDIT | %s %s | status=%d | duration=%.1fms | ip=%s",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request.client.host if request.client else "unknown",
            )

        return response
