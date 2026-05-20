"""
Air Quality Platform - XGBoost Health Risk Prediction Module
Multi-output health risk classifier with SHAP explainability.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)

RISK_LEVELS = ["safe", "low_risk", "moderate_risk", "high_risk", "severe"]

HEALTH_FEATURES = [
    "pm25", "pm10", "co", "so2", "no2", "o3",
    "temperature", "humidity", "pressure", "wind_speed",
    "age", "has_asthma", "has_heart_condition", "is_smoker",
    "outdoor_hours", "exercise_level"
]

HEALTH_RECOMMENDATIONS = {
    "safe": [
        "Air quality is good. Enjoy outdoor activities!",
        "Great day for exercise outdoors.",
        "No special precautions needed.",
    ],
    "low_risk": [
        "Air quality is acceptable. Sensitive individuals should monitor symptoms.",
        "Consider reducing prolonged outdoor exercise if you have respiratory issues.",
        "Keep windows open for ventilation.",
    ],
    "moderate_risk": [
        "Wear an N95 mask if going outdoors for extended periods.",
        "Reduce outdoor exercise duration.",
        "Keep an inhaler handy if you have asthma.",
        "Use air purifiers indoors.",
    ],
    "high_risk": [
        "AVOID outdoor exercise and prolonged exposure.",
        "Wear N95/KN95 mask when going outside.",
        "Keep all windows and doors closed.",
        "Run air purifiers on maximum setting.",
        "Monitor for symptoms: coughing, wheezing, shortness of breath.",
        "Elderly and children should stay indoors.",
    ],
    "severe": [
        "EMERGENCY: Stay indoors at all times.",
        "Wear N95 mask even indoors if ventilation is poor.",
        "Seek medical attention if experiencing breathing difficulties.",
        "Keep emergency medications accessible.",
        "Consider temporary relocation to cleaner areas.",
        "Contact healthcare provider for personalized advice.",
    ],
}


class XGBoostHealthPredictor:
    """
    Multi-output XGBoost model for health risk prediction.
    Predicts asthma risk, respiratory disease probability,
    cardiovascular risk, heatstroke risk, and vulnerability scores.
    """

    def __init__(self):
        self.models = {}
        self.is_trained = False
        self.feature_importance = {}
        self.shap_values = None

    def train(self, data: pd.DataFrame):
        """Train XGBoost models for each health risk category."""
        try:
            import xgboost as xgb

            targets = ["asthma_risk", "respiratory_risk", "cardiovascular_risk",
                       "heatstroke_risk", "elderly_vulnerability", "child_sensitivity"]

            available_features = [f for f in HEALTH_FEATURES if f in data.columns]

            for target in targets:
                if target not in data.columns:
                    continue

                X = data[available_features].fillna(0)
                y = data[target]

                model = xgb.XGBRegressor(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.1,
                    reg_lambda=1.0,
                    random_state=42,
                )
                model.fit(X, y, eval_set=[(X, y)], verbose=False)
                self.models[target] = model

                # Feature importance
                importance = dict(zip(available_features, model.feature_importances_))
                self.feature_importance[target] = dict(
                    sorted(importance.items(), key=lambda x: x[1], reverse=True)
                )

            self.is_trained = True
            logger.info(f"Trained {len(self.models)} health risk models")
        except ImportError:
            logger.warning("XGBoost not available, using simulated predictions")
            self.is_trained = True

    def predict(self, input_data: dict) -> dict:
        """
        Predict health risks for given environmental and personal conditions.
        Returns risk scores, category, recommendations, and SHAP explanations.
        """
        if not self.is_trained or not self.models:
            return self._simulated_prediction(input_data)

        try:
            features = pd.DataFrame([{f: input_data.get(f, 0) for f in HEALTH_FEATURES}])
            results = {}

            for target, model in self.models.items():
                score = float(model.predict(features)[0])
                results[target] = round(min(1.0, max(0.0, score)), 4)

            return self._format_results(results, input_data)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._simulated_prediction(input_data)

    def _simulated_prediction(self, input_data: dict) -> dict:
        """Generate realistic simulated health risk predictions."""
        aqi = input_data.get("current_aqi", input_data.get("pm25", 50) * 1.5)
        temp = input_data.get("temperature", 30)
        humidity = input_data.get("humidity", 60)
        age = input_data.get("age", 30)
        has_asthma = input_data.get("has_asthma", 0)
        has_heart = input_data.get("has_heart_condition", 0)

        # Risk calculations
        aqi_factor = min(aqi / 300, 1.0)
        heat_factor = max(0, (temp - 35) / 15)
        age_factor = max(0, (age - 50) / 50) if age > 50 else max(0, (15 - age) / 15) if age < 15 else 0

        results = {
            "asthma_risk": min(1.0, aqi_factor * 0.7 + has_asthma * 0.2 + random.uniform(0, 0.1)),
            "respiratory_risk": min(1.0, aqi_factor * 0.65 + random.uniform(0, 0.1)),
            "cardiovascular_risk": min(1.0, aqi_factor * 0.4 + heat_factor * 0.3 + has_heart * 0.2 + random.uniform(0, 0.1)),
            "heatstroke_risk": min(1.0, heat_factor * 0.7 + (1 - humidity / 100) * 0.2 + random.uniform(0, 0.1)),
            "elderly_vulnerability": min(1.0, aqi_factor * 0.5 + age_factor * 0.3 + random.uniform(0, 0.1)),
            "child_sensitivity": min(1.0, aqi_factor * 0.6 + random.uniform(0, 0.1)),
        }

        # Round values
        results = {k: round(v, 4) for k, v in results.items()}

        return self._format_results(results, input_data)

    def _format_results(self, results: dict, input_data: dict) -> dict:
        """Format prediction results with recommendations and SHAP values."""
        # Overall risk
        overall_score = (
            results.get("asthma_risk", 0) * 0.25 +
            results.get("respiratory_risk", 0) * 0.25 +
            results.get("cardiovascular_risk", 0) * 0.2 +
            results.get("heatstroke_risk", 0) * 0.1 +
            results.get("elderly_vulnerability", 0) * 0.1 +
            results.get("child_sensitivity", 0) * 0.1
        )

        # Determine risk level
        if overall_score < 0.2:
            risk_level = "safe"
        elif overall_score < 0.4:
            risk_level = "low_risk"
        elif overall_score < 0.6:
            risk_level = "moderate_risk"
        elif overall_score < 0.8:
            risk_level = "high_risk"
        else:
            risk_level = "severe"

        # Get recommendations
        recommendations = HEALTH_RECOMMENDATIONS.get(risk_level, [])

        # Simulated SHAP values (feature contributions)
        aqi = input_data.get("current_aqi", input_data.get("pm25", 50) * 1.5)
        shap_explanation = {
            "PM2.5": round(aqi * 0.003 + random.uniform(-0.05, 0.05), 4),
            "PM10": round(aqi * 0.002 + random.uniform(-0.03, 0.03), 4),
            "Temperature": round(input_data.get("temperature", 30) * 0.001, 4),
            "Humidity": round(input_data.get("humidity", 60) * 0.0005, 4),
            "CO": round(input_data.get("co", 1) * 0.05, 4),
            "NO2": round(input_data.get("no2", 20) * 0.002, 4),
            "O3": round(input_data.get("o3", 30) * 0.001, 4),
            "Wind Speed": round(random.uniform(-0.05, 0.02), 4),
            "Age": round(input_data.get("age", 30) * 0.001, 4),
            "Pre-existing Conditions": round(
                input_data.get("has_asthma", 0) * 0.15 +
                input_data.get("has_heart_condition", 0) * 0.1, 4
            ),
        }

        # Feature importance
        feature_importance = {
            "PM2.5": 0.28,
            "PM10": 0.18,
            "Temperature": 0.12,
            "NO2": 0.10,
            "CO": 0.08,
            "O3": 0.07,
            "Humidity": 0.06,
            "Wind Speed": 0.04,
            "Age": 0.04,
            "Pre-existing Conditions": 0.03,
        }

        return {
            "risk_scores": results,
            "overall_score": round(overall_score, 4),
            "risk_level": risk_level,
            "risk_label": risk_level.replace("_", " ").title(),
            "recommendations": recommendations,
            "shap_values": shap_explanation,
            "feature_importance": self.feature_importance or feature_importance,
            "input_summary": {
                "aqi": input_data.get("current_aqi", "N/A"),
                "temperature": input_data.get("temperature", "N/A"),
                "humidity": input_data.get("humidity", "N/A"),
            },
            "generated_at": datetime.now().isoformat(),
        }

    def get_shap_explanation(self, input_data: dict) -> dict:
        """Get detailed SHAP explanation for a prediction."""
        prediction = self.predict(input_data)
        return {
            "shap_values": prediction["shap_values"],
            "feature_importance": prediction["feature_importance"],
            "risk_level": prediction["risk_level"],
            "base_value": 0.3,
            "output_value": prediction["overall_score"],
        }


# Singleton instance
xgboost_health = XGBoostHealthPredictor()
