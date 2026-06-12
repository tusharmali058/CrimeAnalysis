"""
Network service + router — graph APIs for CriminalNetwork.tsx.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.db.session import get_db
from app.accused.models import Accused
from app.networks.schemas import (
    GraphEdge,
    GraphNode,
    NetworkAnalyticsResponse,
    NetworkGraphResponse,
    NodeDetailResponse,
)
from app.networks import networkx_analytics as nxa

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/networks", tags=["Criminal Networks"])


@router.get("/graph", response_model=NetworkGraphResponse)
async def get_network_graph(
    accused_id: Optional[str] = Query(None, description="Center node accused ID"),
    depth: int = Query(2, ge=1, le=3),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get criminal network graph.
    Returns nodes and edges matching CriminalNetwork.tsx format.
    """
    # Try Neo4j first, fallback to SQL-based graph
    try:
        return await _get_graph_from_neo4j(accused_id, depth)
    except Exception as e:
        logger.info("Neo4j unavailable, falling back to SQL graph: %s", e)
        return await _get_graph_from_sql(db, accused_id)


async def _get_graph_from_neo4j(accused_id: str | None, depth: int) -> NetworkGraphResponse:
    """Extract graph from Neo4j."""
    from app.db.neo4j_driver import run_cypher

    if accused_id:
        query = """
        MATCH (center:Accused {accused_id: $accused_id})
        OPTIONAL MATCH (center)-[r]-(connected)
        RETURN center, r, connected
        LIMIT 50
        """
        records = await run_cypher(query, {"accused_id": accused_id})
    else:
        query = """
        MATCH (a:Accused)-[r]-(b)
        RETURN a, r, b LIMIT 100
        """
        records = await run_cypher(query)

    # Convert to graph format
    nodes_dict = {}
    edges = []

    for record in records:
        for key in ["center", "a", "connected", "b"]:
            if key in record and record[key]:
                node_data = record[key]
                if isinstance(node_data, dict):
                    nid = node_data.get("accused_id") or node_data.get("id") or str(id(node_data))
                    if nid not in nodes_dict:
                        nodes_dict[nid] = {
                            "id": nid,
                            "label": node_data.get("name", nid),
                            "type": node_data.get("type", "accused"),
                            "incidents": node_data.get("incidents", 0),
                        }

    # Build NetworkX graph and compute layout
    node_list = list(nodes_dict.values())
    if node_list:
        G = nxa.build_graph(node_list, [])
        positions = nxa.compute_spring_layout(G)
        stats = nxa.get_graph_stats(G)
    else:
        positions = {}
        stats = {}

    graph_nodes = []
    for n in node_list:
        pos = positions.get(n["id"], (380, 240))
        graph_nodes.append(GraphNode(
            id=n["id"],
            label=n["label"],
            type=n["type"],
            incidents=n.get("incidents", 0),
            x=pos[0],
            y=pos[1],
            radius=max(12, min(24, 10 + n.get("incidents", 0) * 1.5)),
        ))

    return NetworkGraphResponse(nodes=graph_nodes, edges=edges, stats=stats)


async def _get_graph_from_sql(db: AsyncSession, accused_id: str | None) -> NetworkGraphResponse:
    """Build graph from SQL accused relationships (fallback)."""
    query = select(Accused).order_by(Accused.risk_score.desc()).limit(30)
    if accused_id:
        # Get the accused and their associates
        center = await db.execute(
            select(Accused).where(Accused.accused_id == accused_id)
        )
        center_accused = center.scalar_one_or_none()
        if center_accused and center_accused.associate_ids:
            assoc_ids = center_accused.associate_ids
            if isinstance(assoc_ids, list):
                query = select(Accused).where(
                    Accused.accused_id.in_([accused_id] + assoc_ids)
                )

    result = await db.execute(query)
    accused_list = list(result.scalars().all())

    if not accused_list:
        return NetworkGraphResponse(nodes=[], edges=[], stats={})

    # Build nodes
    node_list = []
    for a in accused_list:
        node_list.append({
            "id": a.accused_id,
            "label": a.name,
            "type": "accused",
            "incidents": a.incident_count,
        })

    # Build edges from associate_ids
    edge_list = []
    for a in accused_list:
        if a.associate_ids and isinstance(a.associate_ids, list):
            for assoc_id in a.associate_ids:
                if any(n["id"] == assoc_id for n in node_list):
                    edge_list.append({
                        "source": a.accused_id,
                        "target": assoc_id,
                        "label": "co-accused",
                        "weight": 2,
                    })

    # Add district as location nodes
    districts = set(a.district for a in accused_list)
    for d in districts:
        node_list.append({
            "id": f"loc-{d}",
            "label": d,
            "type": "location",
            "incidents": sum(1 for a in accused_list if a.district == d),
        })
        for a in accused_list:
            if a.district == d:
                edge_list.append({
                    "source": a.accused_id,
                    "target": f"loc-{d}",
                    "label": "operates",
                    "weight": 1,
                })

    # Compute layout
    G = nxa.build_graph(node_list, edge_list)
    positions = nxa.compute_spring_layout(G)
    stats = nxa.get_graph_stats(G)

    graph_nodes = []
    for n in node_list:
        pos = positions.get(n["id"], (380, 240))
        graph_nodes.append(GraphNode(
            id=n["id"],
            label=n["label"],
            type=n["type"],
            incidents=n.get("incidents", 0),
            x=pos[0],
            y=pos[1],
            radius=max(12, min(24, 10 + n.get("incidents", 0) * 1.5)),
        ))

    graph_edges = [
        GraphEdge(source=e["source"], target=e["target"], label=e["label"], weight=e["weight"])
        for e in edge_list
    ]

    return NetworkGraphResponse(nodes=graph_nodes, edges=graph_edges, stats=stats)


@router.get("/analytics", response_model=NetworkAnalyticsResponse)
async def get_network_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get network analytics — centrality, communities, key nodes."""
    # Build graph from SQL
    graph_resp = await _get_graph_from_sql(db, None)

    nodes = [{"id": n.id, "label": n.label, "type": n.type} for n in graph_resp.nodes]
    edges = [{"source": e.source, "target": e.target, "label": e.label, "weight": e.weight} for e in graph_resp.edges]

    G = nxa.build_graph(nodes, edges)

    centrality = nxa.compute_centrality(G)
    communities = nxa.detect_communities(G)
    key_nodes = nxa.get_key_nodes(G)
    stats = nxa.get_graph_stats(G)

    return NetworkAnalyticsResponse(
        centrality=centrality.get("pagerank", {}),
        communities=communities,
        key_nodes=key_nodes,
        stats=stats,
    )


@router.get("/search")
async def search_network_nodes(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search network nodes by name or ID."""
    from sqlalchemy import or_
    result = await db.execute(
        select(Accused)
        .where(
            or_(
                Accused.name.ilike(f"%{q}%"),
                Accused.accused_id.ilike(f"%{q}%"),
            )
        )
        .limit(10)
    )
    accused = result.scalars().all()
    return [
        {"id": a.accused_id, "label": a.name, "type": "accused", "incidents": a.incident_count}
        for a in accused
    ]
