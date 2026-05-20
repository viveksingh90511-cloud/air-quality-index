"""
Air Quality Platform - Flask ML Serving API
Lightweight Flask server for ML model inference endpoints.
Complements FastAPI for batch/offline prediction tasks.
"""

import os
import sys
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])


# ─────────────────────────── ROOT ────────────────────────────

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "Air Quality ML API (Flask)",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/ml/forecast", "/ml/health-risk", "/ml/classify-alert",
            "/ml/hotspots", "/ml/chat", "/ml/rl-alert", "/ml/satellite",
            "/ml/recommendations", "/ml/model-status"
        ]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "flask-ml", "timestamp": datetime.now().isoformat()})


# ─────────────────────────── FORECAST ────────────────────────

@app.route("/ml/forecast", methods=["POST"])
def ml_forecast():
    """AQI forecast via LSTM + Prophet ensemble."""
    data = request.get_json(silent=True) or {}
    horizon = data.get("horizon", "24h")
    station_id = data.get("station_id", "DEL001")

    from backend.ml_models.model_manager import model_manager
    result = model_manager.predict_aqi(horizon=horizon, station_id=station_id)
    return jsonify(result)


@app.route("/ml/batch-forecast", methods=["POST"])
def batch_forecast():
    """Batch AQI forecast for multiple stations."""
    data = request.get_json(silent=True) or {}
    stations = data.get("stations", ["DEL001", "MUM001", "BLR001"])
    horizon = data.get("horizon", "24h")

    from backend.ml_models.model_manager import model_manager
    results = {}
    for sid in stations:
        results[sid] = model_manager.predict_aqi(horizon=horizon, station_id=sid)

    return jsonify({"stations": results, "total": len(results), "horizon": horizon})


# ─────────────────────────── HEALTH RISK ─────────────────────

@app.route("/ml/health-risk", methods=["POST"])
def ml_health_risk():
    """Health risk prediction using XGBoost."""
    data = request.get_json(silent=True) or {}
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.predict_health_risk(data))


@app.route("/ml/disease-probability", methods=["GET"])
def disease_probability():
    """Disease outbreak probability for a city."""
    city = request.args.get("city", "Delhi")
    import random
    aqi_map = {"Delhi": 250, "Mumbai": 130, "Bangalore": 75, "Kolkata": 160, "Chennai": 85}
    aqi = aqi_map.get(city, 100)
    factor = min(aqi / 300, 1.0)

    return jsonify({
        "city": city,
        "current_aqi": aqi,
        "disease_probabilities": {
            "asthma_exacerbation": round(factor * 0.65 + random.uniform(0, 0.08), 3),
            "respiratory_infection": round(factor * 0.45 + random.uniform(0, 0.07), 3),
            "cardiovascular_event": round(factor * 0.30 + random.uniform(0, 0.05), 3),
            "allergic_rhinitis": round(factor * 0.50 + random.uniform(0, 0.08), 3),
        },
        "generated_at": datetime.now().isoformat(),
    })


# ─────────────────────────── ALERTS ──────────────────────────

@app.route("/ml/classify-alert", methods=["POST"])
def classify_alert():
    """Classify alert level using SVM + RF ensemble."""
    data = request.get_json(silent=True) or {}
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.classify_alert(data))


@app.route("/ml/rl-alert", methods=["POST"])
def rl_alert():
    """RL-powered adaptive alert classification."""
    data = request.get_json(silent=True) or {}
    aqi = float(data.get("aqi", 150))
    trend = data.get("trend", "stable")

    from backend.ml_models.rl_alerts import rl_alert_system
    return jsonify(rl_alert_system.classify_alert(aqi, trend))


@app.route("/ml/rl-policy", methods=["GET"])
def rl_policy():
    """Get the learned RL alerting policy."""
    from backend.ml_models.rl_alerts import rl_alert_system
    return jsonify(rl_alert_system.get_policy_summary())


# ─────────────────────────── CLUSTERING ──────────────────────

@app.route("/ml/hotspots", methods=["GET"])
def hotspots():
    """Pollution hotspot detection via K-Means + DBSCAN."""
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.detect_hotspots())


# ─────────────────────────── SATELLITE ───────────────────────

@app.route("/ml/satellite", methods=["GET"])
def satellite():
    """CNN satellite pollution analysis."""
    lat = float(request.args.get("lat", 28.61))
    lng = float(request.args.get("lng", 77.21))
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.analyze_satellite(lat=lat, lng=lng))


# ─────────────────────────── CHATBOT ─────────────────────────

@app.route("/ml/chat", methods=["POST"])
def chat():
    """NLP health assistant chatbot."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    context = {k: v for k, v in data.items() if k != "message"}
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.chat(message, context))


# ─────────────────────────── RECOMMENDATIONS ─────────────────

@app.route("/ml/recommendations", methods=["POST"])
def recommendations():
    """Multi-criteria smart recommendations."""
    data = request.get_json(silent=True) or {}
    aqi = float(data.get("current_aqi", 100))
    rec_type = data.get("type", "outdoor")

    from backend.ml_models.recommendation_engine import recommendation_engine

    if rec_type == "travel":
        return jsonify(recommendation_engine.get_travel_recommendations(aqi))
    elif rec_type == "mask":
        return jsonify(recommendation_engine.get_mask_recommendation(aqi))
    elif rec_type == "outdoor":
        temp = float(data.get("temperature", 30))
        humidity = float(data.get("humidity", 60))
        return jsonify(recommendation_engine.get_outdoor_activities(aqi, temp, humidity))
    else:
        return jsonify({"error": f"Unknown recommendation type: {rec_type}"}), 400


# ─────────────────────────── MODEL STATUS ────────────────────

@app.route("/ml/model-status", methods=["GET"])
def model_status():
    """Status of all ML models."""
    from backend.ml_models.model_manager import model_manager
    return jsonify(model_manager.get_status())


# ─────────────────────────── ERROR HANDLERS ──────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500


# ─────────────────────────── MAIN ────────────────────────────

if __name__ == "__main__":
    app.run(
        host=config.APP_HOST,
        port=config.FLASK_PORT,
        debug=config.APP_DEBUG,
        threaded=True,
    )
