"""
Air Quality Platform - FastAPI Main Application
Primary async API server with all route registrations.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("🚀 Starting Air Quality Platform API...")

    # Initialize database
    from backend.database.connection import init_db
    init_db()

    # Initialize model manager
    from backend.ml_models.model_manager import model_manager
    model_manager.initialize()

    logger.info("✅ API ready to serve requests")
    yield
    logger.info("🛑 Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="Air Quality Forecasting & Health Monitoring Platform",
    description="Enterprise AI-powered environmental intelligence system with real-time monitoring, "
                "AQI forecasting, health analytics, smart alerting, and geospatial intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS + ["*"],  # Allow all in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== REGISTER ROUTES =====================

from backend.fastapi_services.routes.auth import router as auth_router
from backend.fastapi_services.routes.forecast import router as forecast_router
from backend.fastapi_services.routes.health import router as health_router
from backend.fastapi_services.routes.alerts import router as alerts_router
from backend.fastapi_services.routes.analytics import router as analytics_router
from backend.fastapi_services.routes.chatbot import router as chatbot_router
from backend.fastapi_services.routes.recommendations import router as recommendations_router
from backend.fastapi_services.routes.websocket import router as ws_router

app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(forecast_router, prefix="/api", tags=["Forecasting"])
app.include_router(health_router, prefix="/api", tags=["Health Risk"])
app.include_router(alerts_router, prefix="/api", tags=["Alerts"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(chatbot_router, prefix="/api", tags=["AI Chatbot"])
app.include_router(recommendations_router, prefix="/api", tags=["Recommendations"])
app.include_router(ws_router, tags=["WebSocket"])


# ===================== ROOT ENDPOINTS =====================

@app.get("/", tags=["System"])
async def root():
    """API root endpoint."""
    return {
        "name": "Air Quality Forecasting & Health Monitoring Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/register, /api/login, /api/logout",
            "forecast": "/api/predict-aqi, /api/forecast-week, /api/forecast-month",
            "health": "/api/health-risk, /api/disease-probability",
            "alerts": "/api/send-alert, /api/critical-zones",
            "analytics": "/api/heatmap, /api/clusters, /api/trends",
            "chatbot": "/api/chat",
            "recommendations": "/api/recommendations/*",
        },
    }


@app.get("/health", tags=["System"])
async def health_check():
    """System health check."""
    from backend.database.connection import check_connection
    from backend.ml_models.model_manager import model_manager

    db_ok = check_connection()
    models = model_manager.get_status()

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "models": models,
        "environment": config.APP_ENV,
    }


@app.get("/api/stations", tags=["Data"])
async def get_stations():
    """Get all monitoring stations."""
    from backend.utils.data_generator import STATIONS
    return {"stations": STATIONS, "total": len(STATIONS)}


@app.get("/api/realtime", tags=["Data"])
async def get_realtime_data():
    """Get real-time AQI data for all stations."""
    from backend.utils.api_clients import AQICNClient
    client = AQICNClient(config.AQICN_API_KEY)
    from backend.utils.data_generator import STATIONS

    data = []
    for station in STATIONS:
        reading = client.get_station_data(station["lat"], station["lng"])
        reading["station_id"] = station["id"]
        reading["station_name"] = station["name"]
        reading["city"] = station["city"]
        data.append(reading)

    return {"data": data, "total": len(data)}


# ===================== ERROR HANDLERS =====================

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Endpoint not found", "path": str(request.url)})


@app.exception_handler(500)
async def server_error(request: Request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ===================== RUN =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.fastapi_services.main:app",
        host=config.APP_HOST,
        port=config.FASTAPI_PORT,
        reload=config.APP_DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
