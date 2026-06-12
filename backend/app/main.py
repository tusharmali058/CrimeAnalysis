"""
KSP Crime Intelligence Platform — FastAPI Application Entry Point.
All routers are registered here. CORS, middleware, and lifecycle events configured.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.audit import AuditMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🚀 Starting %s [%s]", settings.app_name, settings.app_env)

    # ── Startup ──────────────────────────────────────────────────────────
    from app.db.session import init_db

    try:
        await init_db()
        logger.info("✅ PostgreSQL tables initialized")
    except Exception as e:
        logger.warning("⚠️  PostgreSQL not available: %s", e)

    try:
        from app.db.neo4j_driver import get_neo4j_driver
        await get_neo4j_driver()
        logger.info("✅ Neo4j connected")
    except Exception as e:
        logger.warning("⚠️  Neo4j not available: %s", e)

    try:
        from app.db.redis_client import get_redis
        await get_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning("⚠️  Redis not available: %s", e)

    try:
        from app.db.chromadb_client import get_chromadb_client
        get_chromadb_client()
        logger.info("✅ ChromaDB connected")
    except Exception as e:
        logger.warning("⚠️  ChromaDB not available: %s", e)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    from app.db.session import close_db
    from app.db.neo4j_driver import close_neo4j
    from app.db.redis_client import close_redis

    await close_db()
    await close_neo4j()
    await close_redis()
    logger.info("🛑 %s shut down", settings.app_name)


# ── Create FastAPI app ───────────────────────────────────────────────────

app = FastAPI(
    title="KSP Crime Intelligence Platform API",
    description=(
        "AI-powered Crime Intelligence Platform for Karnataka State Police.\n\n"
        "Provides REST APIs for:\n"
        "- 🔐 Authentication & RBAC\n"
        "- 🤖 Conversational AI (Gemini-powered)\n"
        "- 📊 Crime Analytics & Dashboard\n"
        "- 🕸️ Criminal Network Graph Analysis\n"
        "- 👤 Offender Profiling & Risk Scoring\n"
        "- 📈 Crime Forecasting\n"
        "- 💰 Financial Crime Analysis\n"
        "- 🔍 Investigator Assistant\n"
        "- 📋 Audit Logging"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Store debug flag for middleware
app.state.debug = settings.debug

# ── Middleware (order matters: last added = first executed) ───────────────

# Error handler (outermost)
app.add_middleware(ErrorHandlerMiddleware)

# Audit logging
app.add_middleware(AuditMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# ── Register all routers ─────────────────────────────────────────────────

from app.auth.router import router as auth_router
from app.fir.router import router as fir_router
from app.accused.router import router as accused_router
from app.victims.router import router as victims_router
from app.incidents.router import router as incidents_router
from app.chat.router import router as chat_router
from app.networks.router import router as networks_router
from app.dashboard.router import router as dashboard_router
from app.analytics.router import router as analytics_router
from app.profiles.router import router as profiles_router
from app.investigation.router import router as investigation_router
from app.forecast.router import router as forecast_router
from app.financial.router import router as financial_router
from app.alerts.models import router as alerts_router
from app.audit.models import router as audit_router

prefix = settings.api_prefix

app.include_router(auth_router, prefix=prefix)
app.include_router(fir_router, prefix=prefix)
app.include_router(accused_router, prefix=prefix)
app.include_router(victims_router, prefix=prefix)
app.include_router(incidents_router, prefix=prefix)
app.include_router(chat_router, prefix=prefix)
app.include_router(networks_router, prefix=prefix)
app.include_router(dashboard_router, prefix=prefix)
app.include_router(analytics_router, prefix=prefix)
app.include_router(profiles_router, prefix=prefix)
app.include_router(investigation_router, prefix=prefix)
app.include_router(forecast_router, prefix=prefix)
app.include_router(financial_router, prefix=prefix)
app.include_router(alerts_router, prefix=prefix)
app.include_router(audit_router, prefix=prefix)


# ── Root health check ────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with service status."""
    health = {
        "status": "healthy",
        "services": {},
    }

    # Check PostgreSQL
    try:
        from app.db.session import get_db_context
        async with get_db_context() as db:
            from sqlalchemy import text
            await db.execute(text("SELECT 1"))
        health["services"]["postgresql"] = "connected"
    except Exception:
        health["services"]["postgresql"] = "disconnected"

    # Check Neo4j
    try:
        from app.db.neo4j_driver import run_cypher
        await run_cypher("RETURN 1 AS n")
        health["services"]["neo4j"] = "connected"
    except Exception:
        health["services"]["neo4j"] = "disconnected"

    # Check Redis
    try:
        from app.db.redis_client import get_redis
        r = await get_redis()
        await r.ping()
        health["services"]["redis"] = "connected"
    except Exception:
        health["services"]["redis"] = "disconnected"

    return health
