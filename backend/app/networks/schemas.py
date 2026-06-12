"""
Network schemas — matches CriminalNetwork.tsx Node/Edge interfaces.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    """Matches CriminalNetwork.tsx Node interface."""
    id: str
    label: str
    type: str  # accused, victim, location, financial, gang
    incidents: int = 0
    x: float = 0
    y: float = 0
    radius: float = 14


class GraphEdge(BaseModel):
    """Matches CriminalNetwork.tsx Edge interface."""
    source: str  # 'from' in frontend
    target: str  # 'to' in frontend
    label: str
    weight: int = 1


class NetworkGraphResponse(BaseModel):
    """Full graph response for CriminalNetwork.tsx."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, Any] = {}


class NetworkAnalyticsResponse(BaseModel):
    """NetworkX analytics results."""
    centrality: Dict[str, float] = {}
    communities: List[List[str]] = []
    key_nodes: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {}


class NodeDetailResponse(BaseModel):
    """Detailed info for a single node."""
    id: str
    label: str
    type: str
    incidents: int
    connections: List[Dict[str, Any]] = []
    analytics: Dict[str, Any] = {}
