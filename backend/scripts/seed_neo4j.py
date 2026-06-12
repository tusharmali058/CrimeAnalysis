"""
Seed Neo4j graph database with crime network relationships.
Creates nodes for Accused, FIRs, Locations, and relationships between them.

Usage:
    python -m scripts.seed_neo4j
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def seed_neo4j():
    """Populate Neo4j with crime network graph data."""
    from app.db.neo4j_driver import run_cypher, run_cypher_write
    from app.db.session import get_db_context
    from app.accused.models import Accused
    from app.fir.models import FIR
    from sqlalchemy import select

    print("🔗 Seeding Neo4j graph database...")

    # Clear existing data
    try:
        await run_cypher_write("MATCH (n) DETACH DELETE n")
        print("   🗑️  Cleared existing graph data")
    except Exception as e:
        print(f"   ⚠️  Could not clear Neo4j: {e}")
        return

    # Create constraints
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Accused) REQUIRE a.accused_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (f:FIR) REQUIRE f.fir_number IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
    ]
    for c in constraints:
        try:
            await run_cypher_write(c)
        except Exception:
            pass
    print("   ✅ Constraints created")

    # Fetch data from PostgreSQL
    async with get_db_context() as db:
        accused_result = await db.execute(select(Accused))
        accused_list = accused_result.scalars().all()

        fir_result = await db.execute(select(FIR))
        fir_list = fir_result.scalars().all()

    print(f"   📥 Importing {len(accused_list)} accused, {len(fir_list)} FIRs")

    # Create Location nodes
    districts = set()
    for a in accused_list:
        districts.add(a.district)
    for f in fir_list:
        districts.add(f.district)

    for district in districts:
        await run_cypher_write(
            "MERGE (l:Location {name: $name}) SET l.type = 'district'",
            {"name": district},
        )
    print(f"   ✅ {len(districts)} Location nodes created")

    # Create Accused nodes
    for a in accused_list:
        await run_cypher_write(
            """
            MERGE (acc:Accused {accused_id: $accused_id})
            SET acc.name = $name,
                acc.district = $district,
                acc.status = $status,
                acc.risk_score = $risk_score,
                acc.incidents = $incidents,
                acc.category = $category
            """,
            {
                "accused_id": a.accused_id,
                "name": a.name,
                "district": a.district,
                "status": a.status.value if a.status else "unknown",
                "risk_score": a.risk_score,
                "incidents": a.incident_count,
                "category": a.category or "",
            },
        )
        # Link to Location
        await run_cypher_write(
            """
            MATCH (acc:Accused {accused_id: $accused_id})
            MATCH (l:Location {name: $district})
            MERGE (acc)-[:OPERATES_IN]->(l)
            """,
            {"accused_id": a.accused_id, "district": a.district},
        )
    print(f"   ✅ {len(accused_list)} Accused nodes created + linked to locations")

    # Create CO_ACCUSED relationships from associate_ids
    link_count = 0
    for a in accused_list:
        if a.associate_ids and isinstance(a.associate_ids, list):
            for assoc_id in a.associate_ids[:5]:  # Limit connections
                try:
                    await run_cypher_write(
                        """
                        MATCH (a1:Accused {accused_id: $id1})
                        MATCH (a2:Accused {accused_id: $id2})
                        MERGE (a1)-[:CO_ACCUSED]->(a2)
                        """,
                        {"id1": a.accused_id, "id2": assoc_id},
                    )
                    link_count += 1
                except Exception:
                    pass
    print(f"   ✅ {link_count} CO_ACCUSED relationships created")

    # Create FIR nodes and link
    for f in fir_list[:200]:  # Limit for performance
        await run_cypher_write(
            """
            MERGE (fir:FIR {fir_number: $fir_number})
            SET fir.crime_type = $crime_type,
                fir.district = $district,
                fir.status = $status,
                fir.date = $date
            """,
            {
                "fir_number": f.fir_number,
                "crime_type": f.crime_type,
                "district": f.district,
                "status": f.status.value if f.status else "registered",
                "date": str(f.date_filed),
            },
        )
        # Link FIR to location
        await run_cypher_write(
            """
            MATCH (fir:FIR {fir_number: $fir_number})
            MATCH (l:Location {name: $district})
            MERGE (fir)-[:OCCURRED_AT]->(l)
            """,
            {"fir_number": f.fir_number, "district": f.district},
        )

    # Link Accused to FIRs
    for a in accused_list:
        if a.fir_id:
            fir = next((f for f in fir_list if f.id == a.fir_id), None)
            if fir:
                await run_cypher_write(
                    """
                    MATCH (acc:Accused {accused_id: $accused_id})
                    MATCH (fir:FIR {fir_number: $fir_number})
                    MERGE (acc)-[:ACCUSED_IN]->(fir)
                    """,
                    {"accused_id": a.accused_id, "fir_number": fir.fir_number},
                )

    print(f"   ✅ FIR nodes created and linked")

    # Verify
    count_result = await run_cypher("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
    print("\n📊 Graph Summary:")
    for r in count_result:
        print(f"   {r['label']}: {r['count']} nodes")

    rel_count = await run_cypher("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
    for r in rel_count:
        print(f"   {r['type']}: {r['count']} relationships")

    print("\n✨ Neo4j seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_neo4j())
