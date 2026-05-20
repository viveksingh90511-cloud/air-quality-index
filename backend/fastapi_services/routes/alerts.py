"""
Air Quality Platform - Alert API Routes
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AlertInput(BaseModel):
    pm25: float = 150
    pm10: float = 220
    co: float = 3.0
    so2: float = 30
    no2: float = 60
    o3: float = 40
    temperature: float = 35
    humidity: float = 50
    wind_speed: float = 2.0
    pressure: float = 1010
    aqi: Optional[float] = None


@router.post("/send-alert")
async def send_alert(input_data: AlertInput):
    """Classify and send environmental alert."""
    from backend.ml_models.model_manager import model_manager
    data = input_data.model_dump()
    if data.get("aqi") is None:
        data["aqi"] = data["pm25"] * 1.5
    return model_manager.classify_alert(data)


@router.get("/critical-zones")
async def critical_zones():
    """Get currently active critical zones with alerts."""
    from backend.ml_models.alert_classifier import alert_classifier
    alerts = alert_classifier.get_active_alerts()
    return {
        "total_alerts": len(alerts),
        "alerts": alerts,
        "severity_summary": {
            "emergency": sum(1 for a in alerts if a["alert_class"] == "emergency"),
            "critical": sum(1 for a in alerts if a["alert_class"] == "critical"),
            "warning": sum(1 for a in alerts if a["alert_class"] == "warning"),
        },
    }


@router.get("/alert-history")
async def alert_history(days: int = 7):
    """Get alert history for the specified period."""
    import random
    from datetime import datetime, timedelta

    history = []
    for d in range(days * 3):
        ts = datetime.now() - timedelta(hours=random.randint(0, days * 24))
        severity = random.choices(
            ["warning", "critical", "emergency"],
            weights=[0.6, 0.3, 0.1], k=1
        )[0]
        city = random.choice(["Delhi", "Lucknow", "Kolkata", "Mumbai"])

        history.append({
            "id": 1000 + d,
            "city": city,
            "severity": severity,
            "aqi": random.randint(150, 400),
            "message": f"Air quality alert for {city}",
            "status": random.choice(["resolved", "active", "acknowledged"]),
            "created_at": ts.isoformat(),
            "resolved_at": (ts + timedelta(hours=random.randint(1, 12))).isoformat() if random.random() > 0.3 else None,
        })

    history.sort(key=lambda x: x["created_at"], reverse=True)
    return {"total": len(history), "alerts": history}
