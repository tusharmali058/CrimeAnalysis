"""
NetworkX analytics engine — graph algorithms for crime network analysis.
Runs on graph data extracted from Neo4j or SQL.
"""

from __future__ import annotations

import logging
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


def build_graph(nodes: list[dict], edges: list[dict]) -> nx.Graph:
    """Build a NetworkX graph from node/edge lists."""
    G = nx.Graph()
    for node in nodes:
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in edges:
        G.add_edge(
            edge.get("source") or edge.get("from"),
            edge.get("target") or edge.get("to"),
            label=edge.get("label", ""),
            weight=edge.get("weight", 1),
        )
    return G


def compute_centrality(G: nx.Graph) -> dict[str, dict[str, float]]:
    """Compute various centrality measures."""
    if len(G.nodes) == 0:
        return {}

    return {
        "degree": dict(nx.degree_centrality(G)),
        "betweenness": dict(nx.betweenness_centrality(G)),
        "closeness": dict(nx.closeness_centrality(G)),
        "pagerank": dict(nx.pagerank(G, weight="weight")),
    }


def detect_communities(G: nx.Graph) -> list[list[str]]:
    """Detect communities using greedy modularity (Louvain-like)."""
    if len(G.nodes) < 2:
        return [list(G.nodes)]

    try:
        from community import community_louvain
        partition = community_louvain.best_partition(G)
        communities: dict[int, list[str]] = {}
        for node, comm_id in partition.items():
            communities.setdefault(comm_id, []).append(node)
        return list(communities.values())
    except ImportError:
        # Fallback to greedy modularity
        from networkx.algorithms.community import greedy_modularity_communities
        communities = greedy_modularity_communities(G)
        return [list(c) for c in communities]


def find_shortest_path(G: nx.Graph, source: str, target: str) -> list[str]:
    """Find shortest path between two nodes."""
    try:
        return nx.shortest_path(G, source, target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


def get_key_nodes(G: nx.Graph, top_n: int = 5) -> list[dict[str, Any]]:
    """Identify key nodes by combined centrality measures."""
    if len(G.nodes) == 0:
        return []

    pagerank = nx.pagerank(G, weight="weight")
    degree = dict(G.degree())
    betweenness = nx.betweenness_centrality(G)

    scores = {}
    for node in G.nodes:
        scores[node] = {
            "id": node,
            "label": G.nodes[node].get("label", node),
            "type": G.nodes[node].get("type", "unknown"),
            "degree": degree.get(node, 0),
            "pagerank": round(pagerank.get(node, 0), 4),
            "betweenness": round(betweenness.get(node, 0), 4),
            "combined_score": round(
                pagerank.get(node, 0) * 0.4
                + (betweenness.get(node, 0)) * 0.3
                + (degree.get(node, 0) / max(1, max(degree.values()))) * 0.3,
                4,
            ),
        }

    sorted_nodes = sorted(scores.values(), key=lambda x: x["combined_score"], reverse=True)
    return sorted_nodes[:top_n]


def compute_spring_layout(G: nx.Graph, width: float = 760, height: float = 480) -> dict[str, tuple[float, float]]:
    """Compute node positions using spring layout, scaled to viewport."""
    if len(G.nodes) == 0:
        return {}

    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

    # Scale to viewport
    positions = {}
    margin = 40
    for node, (x, y) in pos.items():
        positions[node] = (
            round(margin + (x + 1) / 2 * (width - 2 * margin)),
            round(margin + (y + 1) / 2 * (height - 2 * margin)),
        )
    return positions


def get_graph_stats(G: nx.Graph) -> dict[str, Any]:
    """Compute summary statistics for the graph."""
    if len(G.nodes) == 0:
        return {"nodes": 0, "edges": 0}

    return {
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "density": round(nx.density(G), 4),
        "components": nx.number_connected_components(G),
        "avg_degree": round(sum(dict(G.degree()).values()) / len(G.nodes), 2),
        "avg_clustering": round(nx.average_clustering(G), 4),
    }
