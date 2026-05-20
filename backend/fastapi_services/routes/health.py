"""
Air Quality Platform - Health Risk API Routes
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class HealthRiskInput(BaseModel):
    pm25: float = 80
    pm10: float = 120
    co: float = 1.5
    so2: float = 15
    no2: float = 40
    o3: float = 30
    temperature: float = 32
    humidity: float = 65
    pressure: float = 1013
    wind_speed: float = 3.5
    current_aqi: Optional[float] = None
    age: int = 30
    has_asthma: int = 0
    has_heart_condition: int = 0
    is_smoker: int = 0
    outdoor_hours: float = 2
    exercise_level: float = 0.5


@router.post("/health-risk")
async def health_risk(input_data: HealthRiskInput):
    """Predict personal health risk based on environmental and health profile."""
    from backend.ml_models.model_manager import model_manager
    data = input_data.model_dump()
    if data.get("current_aqi") is None:
        data["current_aqi"] = data["pm25"] * 1.5
    return model_manager.predict_health_risk(data)


@router.get("/disease-probability")
async def disease_probability(city: str = "Delhi"):
    """Get disease probability analysis by region."""
    import random
    from datetime import datetime

    aqi_map = {
        "Delhi": 250, "Mumbai": 130, "Bangalore": 75, "Kolkata": 160,
        "Chennai": 85, "Hyderabad": 95, "Pune": 90, "Lucknow": 210,
    }
    aqi = aqi_map.get(city, 100)
    factor = min(aqi / 300, 1.0)

    return {
        "city": city,
        "current_aqi": aqi,
        "disease_probabilities": {
            "asthma_exacerbation": round(factor * 0.65 + random.uniform(0, 0.1), 3),
            "respiratory_infection": round(factor * 0.45 + random.uniform(0, 0.08), 3),
            "cardiovascular_event": round(factor * 0.3 + random.uniform(0, 0.05), 3),
            "allergic_rhinitis": round(factor * 0.5 + random.uniform(0, 0.1), 3),
            "bronchitis": round(factor * 0.35 + random.uniform(0, 0.07), 3),
            "eye_irritation": round(factor * 0.55 + random.uniform(0, 0.1), 3),
        },
        "vulnerable_groups": {
            "children": {"risk_multiplier": 1.5, "affected_population_pct": round(factor * 25 + 5, 1)},
            "elderly": {"risk_multiplier": 1.8, "affected_population_pct": round(factor * 30 + 8, 1)},
            "pregnant_women": {"risk_multiplier": 1.3, "affected_population_pct": round(factor * 15 + 3, 1)},
            "outdoor_workers": {"risk_multiplier": 2.0, "affected_population_pct": round(factor * 40 + 10, 1)},
        },
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/health-shap")
async def health_shap():
    """Get SHAP explainability data for health risk model."""
    from backend.ml_models.xgboost_health import xgboost_health
    input_data = {"pm25": 80, "pm10": 120, "temperature": 32, "humidity": 65, "age": 35}
    return xgboost_health.get_shap_explanation(input_data)
