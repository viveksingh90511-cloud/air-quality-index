"""
Air Quality Platform - Recommendations API Routes
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/recommendations/travel")
async def travel_recommendations(city: str = Query("Delhi"), current_aqi: float = Query(120)):
    """Get best travel time recommendations."""
    from backend.ml_models.recommendation_engine import recommendation_engine
    return recommendation_engine.get_travel_recommendations(current_aqi, location=city)


@router.get("/recommendations/outdoor")
async def outdoor_activities(current_aqi: float = Query(80), temperature: float = Query(30), humidity: float = Query(60)):
    """Get safe outdoor activity recommendations."""
    from backend.ml_models.recommendation_engine import recommendation_engine
    return recommendation_engine.get_outdoor_activities(current_aqi, temperature, humidity)


@router.get("/recommendations/masks")
async def mask_recommendations(current_aqi: float = Query(150), duration: float = Query(1), activity: str = Query("moderate")):
    """Get mask recommendations."""
    from backend.ml_models.recommendation_engine import recommendation_engine
    return recommendation_engine.get_mask_recommendation(current_aqi, duration, activity)


@router.get("/recommendations/routes")
async def safe_routes(
    origin_lat: float = Query(28.61), origin_lng: float = Query(77.21),
    dest_lat: float = Query(28.65), dest_lng: float = Query(77.28)
):
    """Get pollution-safe route recommendations."""
    from backend.ml_models.recommendation_engine import recommendation_engine
    return recommendation_engine.get_safe_routes(
        {"lat": origin_lat, "lng": origin_lng},
        {"lat": dest_lat, "lng": dest_lng}
    )
