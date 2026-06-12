"""
Chat schemas — matches CrimeAIChat.tsx Message interface exactly.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request to send a chat message."""
    content: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None
    language: str = "EN"  # "EN" or "KN"


class ChatMessageResponse(BaseModel):
    """
    Response matching the frontend CrimeAIChat.tsx Message interface:
    {id, role, content, timestamp, citations?, confidence?, followups?}
    """
    id: str
    role: str = "assistant"
    content: str
    timestamp: datetime
    citations: Optional[List[str]] = None
    confidence: Optional[float] = None
    followups: Optional[List[str]] = None


class ChatSessionResponse(BaseModel):
    """Chat session metadata."""
    session_id: str
    title: str
    message_count: int
    created_at: datetime
    last_message_at: datetime


class ChatHistoryResponse(BaseModel):
    """Full chat history for a session."""
    session_id: str
    messages: List[ChatMessageResponse]
    total: int


class ChatExportRequest(BaseModel):
    """Request to export chat as PDF."""
    session_id: str
    include_citations: bool = True
