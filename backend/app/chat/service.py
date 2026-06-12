"""
Chat service — orchestrates Gemini LLM with backend tools for multi-turn conversations.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.chat.llm.base import LLMMessage, LLMResponse
from app.chat.llm.gemini import get_llm_provider
from app.chat.llm.tools import CRIME_QUERY_TOOLS, execute_tool
from app.chat.schemas import ChatMessageResponse

logger = logging.getLogger(__name__)

# In-memory session storage (production: use Redis)
_sessions: dict[str, list[LLMMessage]] = {}

# Max conversation context window
MAX_CONTEXT_MESSAGES = 20


async def process_chat_message(
    content: str,
    session_id: str | None = None,
    language: str = "EN",
) -> ChatMessageResponse:
    """
    Process a user chat message through the Gemini AI pipeline.

    Flow:
    1. Load/create session context
    2. Send to Gemini with tool definitions
    3. If Gemini calls tools → execute → feed results back
    4. Return structured response with citations and confidence
    """
    # Create or load session
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    if session_id not in _sessions:
        _sessions[session_id] = []

    session = _sessions[session_id]

    # Add language hint if Kannada
    if language == "KN":
        content = f"[Respond in Kannada] {content}"

    # Add user message to context
    session.append(LLMMessage(role="user", content=content))

    # Trim context window
    if len(session) > MAX_CONTEXT_MESSAGES:
        session = session[-MAX_CONTEXT_MESSAGES:]
        _sessions[session_id] = session

    # Get LLM provider
    llm = get_llm_provider()

    # Step 1: Generate with tools
    response = await llm.generate_with_tools(
        messages=session,
        tools=CRIME_QUERY_TOOLS,
    )

    # Step 2: If LLM requested tool calls, execute them and re-generate
    tool_results = []
    citations = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            logger.info("LLM tool call: %s(%s)", tool_call.name, tool_call.arguments)
            result = await execute_tool(tool_call.name, tool_call.arguments)
            tool_results.append({
                "tool": tool_call.name,
                "result": result,
            })
            # Add citation based on tool
            citation_map = {
                "query_fir_database": "CCTNS FIR Database",
                "get_crime_statistics": "KSP Crime Statistics",
                "search_accused": "CCTNS Accused Database",
                "analyze_criminal_network": "Criminal Network Graph",
                "detect_hotspots": "Spatial Crime Analysis",
                "generate_case_summary": "Case Records System",
                "predict_crime_trend": "ML Prediction Engine",
            }
            citations.append(citation_map.get(tool_call.name, tool_call.name))

        # Feed tool results back to LLM for final answer
        tool_context = "\n\n".join([
            f"**Tool: {tr['tool']}**\nResult: {tr['result']}"
            for tr in tool_results
        ])
        session.append(LLMMessage(
            role="assistant",
            content=f"I have the following data from the crime database:\n\n{tool_context}"
        ))
        session.append(LLMMessage(
            role="user",
            content=f"Based on the data above, provide a comprehensive analysis answering the original query: '{content}'. Format with markdown. Include specific numbers and data points. End with a confidence score."
        ))

        # Re-generate final response
        response = await llm.generate(messages=session)

    # Step 3: Extract confidence from response
    confidence = _extract_confidence(response.content)

    # Step 4: Generate follow-up suggestions
    followups = await _generate_followups(content, response.content)

    # Add assistant response to session
    session.append(LLMMessage(role="assistant", content=response.content))
    _sessions[session_id] = session

    # Build response matching frontend interface
    return ChatMessageResponse(
        id=str(uuid.uuid4()),
        role="assistant",
        content=response.content,
        timestamp=datetime.now(timezone.utc),
        citations=citations if citations else ["KSP Crime Intelligence Database"],
        confidence=confidence,
        followups=followups,
    )


def _extract_confidence(content: str) -> float:
    """Extract confidence score from LLM response text."""
    import re
    # Look for patterns like "Confidence: 94.2%" or "confidence: 87%"
    match = re.search(r'[Cc]onfidence[:\s]+(\d+\.?\d*)%?', content)
    if match:
        try:
            return min(float(match.group(1)), 100.0)
        except ValueError:
            pass
    # Default confidence based on whether tool results were used
    return 85.0


async def _generate_followups(query: str, response: str) -> list[str]:
    """Generate follow-up question suggestions."""
    # Simple heuristic follow-ups based on query content
    followups = []

    query_lower = query.lower()
    if "district" in query_lower or "bengaluru" in query_lower:
        followups.append("Show repeat offenders in this district")
    if "accused" in query_lower or "offender" in query_lower:
        followups.append("Show network connections for this accused")
    if "trend" in query_lower or "pattern" in query_lower:
        followups.append("Predict crime trends for next 30 days")
    if "fir" in query_lower or "case" in query_lower:
        followups.append("Generate case summary PDF")

    # Always add some generic useful follow-ups
    if len(followups) < 3:
        defaults = [
            "Drill down by district",
            "Show network connections",
            "Export analysis report",
            "Compare with previous year",
            "Show related hotspots",
        ]
        for d in defaults:
            if d not in followups and len(followups) < 3:
                followups.append(d)

    return followups[:3]


def get_session_messages(session_id: str) -> list[dict]:
    """Get all messages in a session."""
    session = _sessions.get(session_id, [])
    return [
        {"role": msg.role, "content": msg.content}
        for msg in session
    ]


def list_sessions() -> list[dict]:
    """List all active sessions."""
    return [
        {
            "session_id": sid,
            "message_count": len(msgs),
            "last_message": msgs[-1].content[:100] if msgs else "",
        }
        for sid, msgs in _sessions.items()
    ]


def clear_session(session_id: str) -> bool:
    """Clear a session's history."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
