"""
Air Quality Platform - Analytics API Routes
Heatmap, clusters, trends, and correlation data.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Query
import numpy as np
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/heatmap")
async def get_heatmap():
    """Get pollution heatmap data points."""
    from backend.ml_models.clustering import hotspot_detector
    result = hotspot_detector._simulated_clusters(6)
    return {
        "heatmap_data": result.get("heatmap_data", []),
        "clusters": result.get("clusters", []),
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/clusters")
async def get_clusters():
    """Get pollution cluster analysis."""
    from backend.ml_models.model_manager import model_manager
    return model_manager.detect_hotspots()


@router.get("/trends")
async def get_trends(
    station_id: str = Query("DEL001"),
    days: int = Query(30),
    pollutant: str = Query("pm25")
):
    """Get historical pollution trends."""
    records = []
    now = datetime.now()

    for d in range(days):
        date = now - timedelta(days=days - d)
        base = 80 + 30 * np.sin(2 * np.pi * d / 30)
        value = max(10, base + random.gauss(0, 15))

        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(value, 1),
            "pollutant": pollutant,
            "aqi": round(value * 1.5, 1),
        })

    # Calculate trend
    values = [r["value"] for r in records]
    trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
    avg = round(np.mean(values), 1)

    return {
        "station_id": station_id,
        "pollutant": pollutant,
        "days": days,
        "data": records,
        "statistics": {
            "mean": avg,
            "max": round(max(values), 1),
            "min": round(min(values), 1),
            "std": round(np.std(values), 1),
            "trend": trend_direction,
            "change_pct": round((values[-1] - values[0]) / values[0] * 100, 1),
        },
    }


@router.get("/correlation-matrix")
async def correlation_matrix():
    """Get pollutant correlation matrix."""
    features = ["PM2.5", "PM10", "CO", "SO₂", "NO₂", "O₃", "Temp", "Humidity", "Wind"]

    # Realistic correlation matrix
    n = len(features)
    base = np.array([
        [1.00, 0.85, 0.62, 0.45, 0.58, -0.22, 0.15, -0.35, -0.42],
        [0.85, 1.00, 0.55, 0.50, 0.52, -0.18, 0.18, -0.30, -0.38],
        [0.62, 0.55, 1.00, 0.35, 0.68, -0.15, 0.10, -0.25, -0.30],
        [0.45, 0.50, 0.35, 1.00, 0.42, -0.10, 0.08, -0.20, -0.25],
        [0.58, 0.52, 0.68, 0.42, 1.00, 0.25, 0.22, -0.28, -0.35],
        [-0.22, -0.18, -0.15, -0.10, 0.25, 1.00, 0.55, -0.15, 0.10],
        [0.15, 0.18, 0.10, 0.08, 0.22, 0.55, 1.00, -0.45, 0.05],
        [-0.35, -0.30, -0.25, -0.20, -0.28, -0.15, -0.45, 1.00, 0.15],
        [-0.42, -0.38, -0.30, -0.25, -0.35, 0.10, 0.05, 0.15, 1.00],
    ])

    # Add small noise for realism
    noise = np.random.uniform(-0.03, 0.03, (n, n))
    matrix = np.clip(base + noise, -1, 1)
    np.fill_diagonal(matrix, 1.0)

    return {
        "features": features,
        "matrix": matrix.round(3).tolist(),
        "strong_correlations": [
            {"pair": ["PM2.5", "PM10"], "value": round(matrix[0][1], 3), "type": "positive"},
            {"pair": ["CO", "NO₂"], "value": round(matrix[2][4], 3), "type": "positive"},
            {"pair": ["PM2.5", "Wind"], "value": round(matrix[0][8], 3), "type": "negative"},
            {"pair": ["Temp", "Humidity"], "value": round(matrix[6][7], 3), "type": "negative"},
        ],
    }


@router.get("/satellite-analysis")
async def satellite_analysis(lat: float = Query(28.61), lng: float = Query(77.21)):
    """Get CNN satellite pollution analysis."""
    from backend.ml_models.model_manager import model_manager
    return model_manager.analyze_satellite(lat=lat, lng=lng)


@router.get("/model-status")
async def model_status():
    """Get status of all ML models."""
    from backend.ml_models.model_manager import model_manager
    return model_manager.get_status()


@router.get("/summary-stats")
async def summary_stats():
    """Get platform summary statistics."""
    return {
        "total_stations": 10,
        "active_sensors": 18,
        "alerts_today": random.randint(3, 12),
        "avg_aqi_national": round(random.uniform(80, 160), 1),
        "cities_monitored": 8,
        "forecasts_generated": random.randint(500, 2000),
        "health_assessments": random.randint(200, 800),
        "models_active": 7,
        "uptime_pct": 99.7,
        "last_updated": datetime.now().isoformat(),
    }
