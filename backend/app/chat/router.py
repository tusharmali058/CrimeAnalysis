"""
Chat API router — endpoints matching CrimeAIChat.tsx.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.chat.schemas import (
    ChatExportRequest,
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
)
from app.chat.service import (
    clear_session,
    get_session_messages,
    list_sessions,
    process_chat_message,
)

router = APIRouter(prefix="/chat", tags=["Chat AI"])


@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a chat message and get AI response.
    Connects to Gemini with access to all backend tools.
    """
    try:
        response = await process_chat_message(
            content=data.content,
            session_id=data.session_id,
            language=data.language,
        )
        return response
    except Exception as e:
        # Fallback response on error
        return ChatMessageResponse(
            id=str(uuid.uuid4()),
            role="assistant",
            content=f"I apologize, but I encountered an error processing your query. Please try again.\n\n*Error: {str(e)}*\n\n*Confidence: 0% · Error logged*",
            timestamp=datetime.now(timezone.utc),
            citations=["System Error Log"],
            confidence=0.0,
            followups=["Try a simpler query", "Check system status"],
        )


@router.get("/sessions", response_model=list[dict])
async def get_sessions(
    current_user: User = Depends(get_current_user),
):
    """List all chat sessions for the current user."""
    return list_sessions()


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get chat history for a session."""
    messages = get_session_messages(session_id)
    return {
        "session_id": session_id,
        "messages": messages,
        "total": len(messages),
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Clear a chat session."""
    if clear_session(session_id):
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/export-pdf")
async def export_chat_pdf(
    data: ChatExportRequest,
    current_user: User = Depends(get_current_user),
):
    """Export chat session as PDF."""
    messages = get_session_messages(data.session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found or empty")

    # Generate PDF using reportlab
    from app.utils.pdf_export import generate_chat_pdf
    pdf_bytes = generate_chat_pdf(messages, data.session_id)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ksp_chat_{data.session_id[:8]}.pdf"
        },
    )
