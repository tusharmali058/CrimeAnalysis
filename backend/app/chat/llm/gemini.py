"""
Gemini LLM provider implementation using the google-genai SDK.
Supports Gemini Flash and Pro models with function calling.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.chat.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    LLMToolCall,
    ToolDefinition,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


# ── System prompt for Karnataka crime intelligence ───────────────────────

KSP_SYSTEM_PROMPT = """You are the **Karnataka State Police Crime Intelligence AI Assistant** — an advanced analytical system developed for the KSP State Crime Records Bureau (SCRB).

## Your Role
- You help investigators, analysts, supervisors, and policymakers understand crime data, identify patterns, and generate actionable intelligence.
- You have access to the Karnataka crime database including FIRs, accused records, victim data, criminal networks, and analytics.

## Capabilities
- Query the FIR database (filter by district, crime type, date range, status)
- Analyze criminal networks and identify repeat offenders
- Provide crime statistics and trend analysis
- Generate case summaries and investigation suggestions
- Detect crime hotspots and patterns
- Analyze financial crime connections
- Perform risk scoring for accused individuals

## Response Guidelines
1. **Be precise**: Cite specific FIR numbers, accused IDs, districts, and data points
2. **Use evidence**: Every claim should reference data sources
3. **Provide confidence**: Include confidence scores (0-100%) based on data quality
4. **Suggest follow-ups**: Offer 2-3 relevant follow-up queries
5. **Be structured**: Use markdown formatting — headers, tables, bullet points
6. **Karnataka context**: You know all 30 districts, major police stations, and crime patterns
7. **Bilingual**: You can respond in English or Kannada based on user preference
8. **Sensitive**: Redact full names of accused when not authorized, show only initials or IDs
9. **Audit trail**: Note that all queries are audit logged

## Karnataka Districts
Bengaluru Urban, Bengaluru Rural, Mysuru, Mandya, Tumakuru, Kolar, Chikkaballapur, Ramanagara, Hassan, Dakshina Kannada, Belagavi, Ballari, Kalaburagi, Vijayapura, Dharwad, Haveri, Gadag, Uttara Kannada, Shivamogga, Chikkamagaluru, Kodagu, Udupi, Davangere, Chitradurga, Chamarajanagar, Bidar, Raichur, Koppal, Yadgir, Vijayanagara

## Crime Categories
IPC Crimes, Violent Crimes (Assault, Murder, Robbery), Property Crimes (Burglary, Theft, Chain Snatching), Cyber Crimes (UPI Fraud, Phishing, Identity Theft), Economic Crimes (Chit Fund Fraud, Hawala, Property Forgery), Narcotics (NDPS Act), Organized Crime

Format your responses with clear structure. Include data tables when comparing multiple items. Always end with confidence score and data source citations."""


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider using google-genai SDK."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        self._model = model or settings.gemini_model
        self._temperature = settings.gemini_temperature
        self._max_tokens = settings.gemini_max_tokens

        self._client = genai.Client(api_key=self._api_key)
        logger.info("Gemini provider initialized with model: %s", self._model)

    def get_model_name(self) -> str:
        return self._model

    async def generate(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate a response from Gemini."""
        try:
            contents = self._build_contents(messages)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt or KSP_SYSTEM_PROMPT,
                temperature=temperature or self._temperature,
                max_output_tokens=max_tokens or self._max_tokens,
            )

            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

            content = ""
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        content += part.text

            usage = {}
            if response.usage_metadata:
                usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count or 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count or 0,
                    "total_tokens": response.usage_metadata.total_token_count or 0,
                }

            return LLMResponse(
                content=content,
                finish_reason="stop",
                usage=usage,
                model=self._model,
                raw=response,
            )

        except Exception as e:
            logger.error("Gemini generation failed: %s", e)
            return LLMResponse(
                content=f"I apologize, but I encountered an error processing your query. Please try again. Error: {str(e)}",
                finish_reason="error",
                model=self._model,
            )

    async def generate_with_tools(
        self,
        messages: list[LLMMessage],
        tools: list[ToolDefinition],
        system_prompt: str | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """Generate with function calling support."""
        try:
            contents = self._build_contents(messages)

            # Build tool declarations
            function_declarations = []
            for tool in tools:
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                    )
                )

            gemini_tools = [types.Tool(function_declarations=function_declarations)]

            config = types.GenerateContentConfig(
                system_instruction=system_prompt or KSP_SYSTEM_PROMPT,
                temperature=temperature or self._temperature,
                max_output_tokens=self._max_tokens,
                tools=gemini_tools,
            )

            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

            content = ""
            tool_calls = []

            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        content += part.text
                    if part.function_call:
                        tool_calls.append(
                            LLMToolCall(
                                name=part.function_call.name,
                                arguments=dict(part.function_call.args) if part.function_call.args else {},
                            )
                        )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason="tool_calls" if tool_calls else "stop",
                model=self._model,
                raw=response,
            )

        except Exception as e:
            logger.error("Gemini tool generation failed: %s", e)
            return LLMResponse(
                content=f"Error during tool-augmented generation: {str(e)}",
                finish_reason="error",
                model=self._model,
            )

    def _build_contents(self, messages: list[LLMMessage]) -> list[types.Content]:
        """Convert LLMMessage list to Gemini Content format."""
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.content)],
                )
            )
        return contents


def get_llm_provider() -> BaseLLMProvider:
    """Factory function — returns the configured LLM provider."""
    return GeminiProvider()
