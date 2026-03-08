"""
Hotel Booking Intelligence API — Main Application

A data-driven RESTful API that provides:
  1. Historical hotel booking data exploration with filters and pagination
  2. Full CRUD for operational incident reports and manager notes
  3. Analytical endpoints for cancellation rates, demand patterns, and market segments
  4. Intelligent insights including risk scoring and operational hotspot detection

Built with FastAPI for automatic OpenAPI documentation, Pydantic validation,
and high performance. Uses SQLAlchemy ORM with SQLite for zero-config portability.

Production features include CORS middleware, rate limiting, structured logging,
and a health-check endpoint for deployment monitoring.

Author: Ali
Module: COMP3011 Web Services and Web Data
Dataset: Hotel Booking Demand (Kaggle)
"""

import logging
import time
import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import engine, Base, SessionLocal
from app.routers import bookings, incidents, notes, analytics, insights
from app.routers import auth_router, ai_insights

# ---------------------------------------------------------------------------
# Structured logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("hotel_api")

# Create all database tables on startup (if they don't exist)
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Rate limiter  (slowapi wraps limits per IP via the Limiter class)
# Default: 60 requests/minute globally — individual routes can override.
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# ---------------------------------------------------------------------------
# Initialise the FastAPI application with metadata for Swagger UI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Hotel Booking Intelligence API",
    description=(
        "RESTful intelligence layer over the "
        "[Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) "
        "dataset (119,390 records).\n\n"
        "| Resource | Description |\n"
        "| --- | --- |\n"
        "| **Bookings** | Browse & filter with pagination |\n"
        "| **Incidents** | CRUD for operational reports |\n"
        "| **Notes** | Manager annotations per booking |\n"
        "| **Analytics** | Cancellation rates, demand trends, segments |\n"
        "| **Insights** | Rule-based risk scoring & hotspots |\n"
        "| **AI Insights** | GPT-powered narrative risk assessments |\n\n"
        "**Auth:** API Key or JWT Bearer — click **Authorize** and enter `hotel-booking-dev-key-2025`\n\n"
        "**Extras:** [Live Dashboard](/dashboard) · "
        "Rate limiting (60/min) · CORS · Health check · "
        "[GitHub](https://github.com/9ali-oop/hotel-booking-api)\n\n"
        "*COMP3011 Web Services — University of Leeds*"
    ),
    version="1.0.0",
    contact={
        "name": "Ali",
        "url": "https://github.com/9ali-oop",
    },
)

# Attach rate limiter to the app — SlowAPIMiddleware enforces limits
# globally on every request without needing per-route decorators.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS middleware — allows the frontend dashboard (and external clients)
# to call the API from any origin during development.  In production the
# allowed_origins list would be locked down to specific domains.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request logging middleware — logs method, path, status, and latency
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s → %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Mount static files directory for the frontend dashboard
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register all routers
app.include_router(auth_router.router)
app.include_router(bookings.router)
app.include_router(incidents.router)
app.include_router(notes.router)
app.include_router(analytics.router)
app.include_router(insights.router)
app.include_router(ai_insights.router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    """
    API root endpoint. Returns a welcome message with links to
    documentation and available resource endpoints.
    """
    return {
        "message": "Hotel Booking Intelligence API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "bookings": "/bookings",
            "incidents": "/incidents",
            "notes": "/notes",
            "analytics": {
                "cancellation_rate": "/analytics/cancellation-rate",
                "monthly_demand": "/analytics/monthly-demand",
                "market_segments": "/analytics/market-segment-performance",
            },
            "insights": {
                "high_risk_bookings": "/insights/high-risk-bookings",
                "operational_hotspots": "/insights/operational-hotspots",
            },
            "dashboard": "/dashboard",
        },
    }


# ---------------------------------------------------------------------------
# Health-check endpoint — useful for Railway / uptime monitors
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Operations"])
def health_check():
    """
    Lightweight health-check endpoint for deployment platforms and
    uptime monitors.  Returns database connectivity status.
    """
    try:
        db = SessionLocal()
        db.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )
        db.close()
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0",
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    """Serve the frontend dashboard."""
    dashboard_path = os.path.join(static_dir, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not available. Place index.html in /static directory."}
