"""
Neo4j async driver singleton.
Provides session-based Cypher query execution.
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from app.config import get_settings

logger = logging.getLogger(__name__)

_driver: AsyncDriver | None = None


async def get_neo4j_driver() -> AsyncDriver:
    """Get or create the Neo4j async driver."""
    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=50,
        )
        # Verify connectivity
        try:
            await _driver.verify_connectivity()
            logger.info("Neo4j connection established: %s", settings.neo4j_uri)
        except Exception as e:
            logger.warning("Neo4j not available: %s (will retry on demand)", e)
    return _driver


async def close_neo4j() -> None:
    """Close the Neo4j driver on shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("Neo4j connection closed")


async def run_cypher(
    query: str,
    parameters: dict[str, Any] | None = None,
    db: str = "neo4j",
) -> list[dict[str, Any]]:
    """
    Execute a Cypher query and return results as a list of dicts.
    
    Args:
        query: Cypher query string
        parameters: Query parameters
        db: Database name
        
    Returns:
        List of record dictionaries
    """
    driver = await get_neo4j_driver()
    async with driver.session(database=db) as session:
        result = await session.run(query, parameters or {})
        records = await result.data()
        return records


async def run_cypher_write(
    query: str,
    parameters: dict[str, Any] | None = None,
    db: str = "neo4j",
) -> dict[str, Any]:
    """
    Execute a write Cypher query within a transaction.
    
    Returns:
        Summary counters dict
    """
    driver = await get_neo4j_driver()
    async with driver.session(database=db) as session:

        async def _work(tx):
            result = await tx.run(query, parameters or {})
            summary = await result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set,
            }

        return await session.execute_write(_work)
