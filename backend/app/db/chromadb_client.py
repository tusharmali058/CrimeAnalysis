"""
ChromaDB client for vector storage and similarity search.
Used for conversation memory and document retrieval.
"""

from __future__ import annotations

import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: chromadb.HttpClient | None = None


def get_chromadb_client() -> chromadb.HttpClient:
    """Get or create the ChromaDB client."""
    global _client
    if _client is None:
        settings = get_settings()
        try:
            _client = chromadb.HttpClient(
                host=settings.chromadb_host,
                port=settings.chromadb_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            # Test connection
            _client.heartbeat()
            logger.info(
                "ChromaDB connection established: %s:%s",
                settings.chromadb_host,
                settings.chromadb_port,
            )
        except Exception as e:
            logger.warning("ChromaDB not available: %s (using in-memory fallback)", e)
            _client = chromadb.Client(
                settings=ChromaSettings(anonymized_telemetry=False)
            )
    return _client


def get_or_create_collection(name: str, metadata: dict[str, Any] | None = None):
    """Get or create a ChromaDB collection."""
    client = get_chromadb_client()
    return client.get_or_create_collection(
        name=name,
        metadata=metadata or {"hnsw:space": "cosine"},
    )


# ── Pre-defined collections ─────────────────────────────────────────────

def get_fir_collection():
    """Collection for FIR document embeddings."""
    return get_or_create_collection(
        "fir_documents",
        metadata={"hnsw:space": "cosine", "description": "FIR document embeddings"},
    )


def get_conversation_collection():
    """Collection for conversation history embeddings."""
    return get_or_create_collection(
        "conversations",
        metadata={"hnsw:space": "cosine", "description": "Chat conversation memory"},
    )


def get_case_collection():
    """Collection for case summary embeddings (for similar case search)."""
    return get_or_create_collection(
        "case_summaries",
        metadata={"hnsw:space": "cosine", "description": "Case summary embeddings"},
    )
