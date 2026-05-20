"""
Air Quality Platform - Model Manager / Orchestrator
Unified model loading, caching, prediction routing, and ensemble management.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Central orchestrator for all ML models.
    Handles model loading, caching, routing, and ensemble predictions.
    """

    def __init__(self):
        self._models = {}
        self._initialized = False

    def initialize(self):
        """Lazy-load all model instances."""
        if self._initialized:
            return

        try:
            from backend.ml_models.lstm_forecaster import lstm_forecaster
            self._models["lstm"] = lstm_forecaster
        except Exception as e:
            logger.warning(f"LSTM model load failed: {e}")

        try:
            from backend.ml_models.xgboost_health import xgboost_health
            self._models["xgboost_health"] = xgboost_health
        except Exception as e:
            logger.warning(f"XGBoost model load failed: {e}")

        try:
            from backend.ml_models.clustering import hotspot_detector
            self._models["clustering"] = hotspot_detector
        except Exception as e:
            logger.warning(f"Clustering model load failed: {e}")

        try:
            from backend.ml_models.alert_classifier import alert_classifier
            self._models["alert_classifier"] = alert_classifier
        except Exception as e:
            logger.warning(f"Alert classifier load failed: {e}")

        try:
            from backend.ml_models.prophet_forecaster import prophet_forecaster
            self._models["prophet"] = prophet_forecaster
        except Exception as e:
            logger.warning(f"Prophet model load failed: {e}")

        try:
            from backend.ml_models.cnn_satellite import cnn_satellite
            self._models["cnn_satellite"] = cnn_satellite
        except Exception as e:
            logger.warning(f"CNN satellite model load failed: {e}")

        try:
            from backend.ml_models.nlp_assistant import nlp_assistant
            self._models["nlp_assistant"] = nlp_assistant
        except Exception as e:
            logger.warning(f"NLP assistant load failed: {e}")

        self._initialized = True
        logger.info(f"ModelManager initialized with {len(self._models)} models")

    def get_model(self, model_name: str):
        """Get a specific model instance."""
        self.initialize()
        return self._models.get(model_name)

    def predict_aqi(self, horizon: str = "24h", station_id: str = None, data=None) -> dict:
        """Route AQI prediction to appropriate model(s)."""
        self.initialize()

        results = {}

        # LSTM prediction
        lstm = self._models.get("lstm")
        if lstm:
            results["lstm"] = lstm.predict(data=data, horizon=horizon, station_id=station_id)

        # Prophet prediction
        prophet = self._models.get("prophet")
        if prophet:
            from backend.ml_models.lstm_forecaster import HORIZONS
            periods = HORIZONS.get(horizon, 24)
            results["prophet"] = prophet.predict(periods=periods, station_id=station_id)

        # Ensemble (hybrid)
        if "lstm" in results and "prophet" in results and prophet:
            lstm_preds = results["lstm"]["predictions"]
            results["ensemble"] = prophet.hybrid_predict(
                lstm_predictions=lstm_preds,
                periods=len(lstm_preds),
                station_id=station_id
            )

        # Return best model or ensemble
        if "ensemble" in results:
            primary = results["ensemble"]
        elif "lstm" in results:
            primary = results["lstm"]
        elif "prophet" in results:
            primary = results["prophet"]
        else:
            primary = {"error": "No forecast models available"}

        return {
            "primary": primary,
            "all_models": {k: v.get("summary", {}) for k, v in results.items()},
            "models_used": list(results.keys()),
            "generated_at": datetime.now().isoformat(),
        }

    def predict_health_risk(self, input_data: dict) -> dict:
        """Route health risk prediction to XGBoost model."""
        self.initialize()
        model = self._models.get("xgboost_health")
        if model:
            return model.predict(input_data)
        return {"error": "Health risk model not available"}

    def classify_alert(self, input_data: dict) -> dict:
        """Route alert classification to SVM/RF ensemble."""
        self.initialize()
        model = self._models.get("alert_classifier")
        if model:
            return model.classify(input_data)
        return {"error": "Alert classifier not available"}

    def detect_hotspots(self, data=None) -> dict:
        """Route hotspot detection to clustering model."""
        self.initialize()
        model = self._models.get("clustering")
        if model:
            return model.detect_hotspots(data)
        return {"error": "Clustering model not available"}

    def analyze_satellite(self, lat: float, lng: float) -> dict:
        """Route satellite analysis to CNN model."""
        self.initialize()
        model = self._models.get("cnn_satellite")
        if model:
            return model.analyze(lat=lat, lng=lng)
        return {"error": "CNN satellite model not available"}

    def chat(self, message: str, context: dict = None) -> dict:
        """Route chat message to NLP assistant."""
        self.initialize()
        model = self._models.get("nlp_assistant")
        if model:
            return model.chat(message, context)
        return {"response": "AI assistant not available", "suggestions": []}

    def get_status(self) -> dict:
        """Get status of all loaded models."""
        self.initialize()
        status = {}
        for name, model in self._models.items():
            status[name] = {
                "loaded": True,
                "type": type(model).__name__,
                "trained": getattr(model, "is_trained", getattr(model, "is_fitted", getattr(model, "is_loaded", False))),
            }
        return {
            "total_models": len(self._models),
            "models": status,
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat(),
        }


# Singleton instance
model_manager = ModelManager()
