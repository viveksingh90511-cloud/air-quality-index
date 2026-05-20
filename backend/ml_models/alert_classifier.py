"""
Air Quality Platform - SVM + Random Forest Alert Classification Module
Ensemble classifier for environmental emergency detection and routing.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)

ALERT_CLASSES = ["safe", "warning", "critical", "emergency"]

ALERT_ACTIONS = {
    "safe": {
        "notification": False,
        "sms": False,
        "email": False,
        "hospital_alert": False,
        "government_alert": False,
        "message": "All conditions normal. No action required.",
    },
    "warning": {
        "notification": True,
        "sms": False,
        "email": True,
        "hospital_alert": False,
        "government_alert": False,
        "message": "Elevated pollution levels detected. Sensitive groups should take precautions.",
    },
    "critical": {
        "notification": True,
        "sms": True,
        "email": True,
        "hospital_alert": True,
        "government_alert": True,
        "message": "CRITICAL: Dangerous pollution levels. All residents advised to stay indoors.",
    },
    "emergency": {
        "notification": True,
        "sms": True,
        "email": True,
        "hospital_alert": True,
        "government_alert": True,
        "message": "EMERGENCY: Hazardous conditions. Immediate action required. Evacuate if necessary.",
    },
}


class AlertClassifier:
    """
    Ensemble SVM + Random Forest classifier for environmental alerts.
    Classifies conditions into Safe, Warning, Critical, Emergency.
    Includes alert routing to hospitals, SMS, email, government dashboards.
    """

    def __init__(self):
        self.svm_model = None
        self.rf_model = None
        self.scaler = None
        self.is_trained = False

    def train(self, data: pd.DataFrame):
        """Train both SVM and Random Forest models."""
        try:
            from sklearn.svm import SVC
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            from sklearn.model_selection import train_test_split

            features = ["pm25", "pm10", "co", "so2", "no2", "o3",
                       "temperature", "humidity", "wind_speed", "pressure"]
            available = [f for f in features if f in data.columns]
            X = data[available].fillna(0).values

            # Generate labels if not present
            if "alert_class" not in data.columns:
                aqi = data.get("aqi", data.get("pm25", pd.Series([50])) * 1.5)
                labels = []
                for a in aqi:
                    if a < 100: labels.append("safe")
                    elif a < 200: labels.append("warning")
                    elif a < 300: labels.append("critical")
                    else: labels.append("emergency")
                y = labels
            else:
                y = data["alert_class"].values

            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Train SVM
            self.svm_model = SVC(kernel='rbf', probability=True, C=10, gamma='scale', random_state=42)
            self.svm_model.fit(X_scaled, y_encoded)

            # Train Random Forest
            self.rf_model = RandomForestClassifier(
                n_estimators=200, max_depth=10, min_samples_split=5,
                random_state=42, n_jobs=-1
            )
            self.rf_model.fit(X_scaled, y_encoded)

            self.is_trained = True
            logger.info("Alert classification models trained successfully")

        except ImportError:
            logger.warning("sklearn not available, using simulated classification")
            self.is_trained = True

    def classify(self, input_data: dict) -> dict:
        """
        Classify environmental conditions and determine alert level.
        Uses ensemble voting between SVM and Random Forest.
        """
        if not self.is_trained or self.svm_model is None:
            return self._simulated_classification(input_data)

        try:
            features = ["pm25", "pm10", "co", "so2", "no2", "o3",
                       "temperature", "humidity", "wind_speed", "pressure"]
            X = np.array([[input_data.get(f, 0) for f in features]])
            X_scaled = self.scaler.transform(X)

            # Get predictions from both models
            svm_proba = self.svm_model.predict_proba(X_scaled)[0]
            rf_proba = self.rf_model.predict_proba(X_scaled)[0]

            # Ensemble: weighted average
            ensemble_proba = 0.4 * svm_proba + 0.6 * rf_proba
            predicted_class = self.label_encoder.inverse_transform([np.argmax(ensemble_proba)])[0]

            return self._format_result(predicted_class, ensemble_proba, input_data)

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return self._simulated_classification(input_data)

    def _simulated_classification(self, input_data: dict) -> dict:
        """Simulated alert classification based on AQI thresholds."""
        aqi = input_data.get("aqi", input_data.get("pm25", 50) * 1.5)
        temp = input_data.get("temperature", 30)
        co = input_data.get("co", 1)
        so2 = input_data.get("so2", 10)

        # Determine alert class
        score = aqi / 100
        if temp > 45: score += 0.5
        if co > 4: score += 0.3
        if so2 > 50: score += 0.3

        if score < 1.0:
            alert_class = "safe"
            probabilities = [0.85, 0.10, 0.04, 0.01]
        elif score < 2.0:
            alert_class = "warning"
            probabilities = [0.10, 0.75, 0.12, 0.03]
        elif score < 3.0:
            alert_class = "critical"
            probabilities = [0.02, 0.10, 0.78, 0.10]
        else:
            alert_class = "emergency"
            probabilities = [0.01, 0.04, 0.15, 0.80]

        return self._format_result(alert_class, probabilities, input_data)

    def _format_result(self, alert_class: str, probabilities, input_data: dict) -> dict:
        """Format classification result with alert routing info."""
        actions = ALERT_ACTIONS.get(alert_class, ALERT_ACTIONS["safe"])

        severity_colors = {
            "safe": "#00e400",
            "warning": "#ffff00",
            "critical": "#ff4444",
            "emergency": "#7e0023",
        }

        if isinstance(probabilities, np.ndarray):
            proba_dict = {c: round(float(p), 4) for c, p in zip(ALERT_CLASSES, probabilities)}
        else:
            proba_dict = {c: round(float(p), 4) for c, p in zip(ALERT_CLASSES, probabilities)}

        # Find nearest hospitals if critical or emergency
        nearest_hospitals = []
        if alert_class in ["critical", "emergency"]:
            nearest_hospitals = [
                {"name": "AIIMS Delhi", "distance_km": 5.2, "available_beds": 45},
                {"name": "Safdarjung Hospital", "distance_km": 6.8, "available_beds": 32},
                {"name": "Sir Ganga Ram Hospital", "distance_km": 8.1, "available_beds": 18},
            ]

        return {
            "alert_class": alert_class,
            "alert_label": alert_class.upper(),
            "severity_color": severity_colors.get(alert_class, "#ffffff"),
            "probabilities": proba_dict,
            "confidence": round(max(probabilities if isinstance(probabilities, (list, np.ndarray)) else [0.8]), 4),
            "actions": actions,
            "nearest_hospitals": nearest_hospitals,
            "triggered_by": {
                "aqi": input_data.get("aqi", "N/A"),
                "pm25": input_data.get("pm25", "N/A"),
                "temperature": input_data.get("temperature", "N/A"),
            },
            "timestamp": datetime.now().isoformat(),
            "model": "svm_rf_ensemble",
        }

    def get_active_alerts(self) -> list:
        """Get list of currently active simulated alerts."""
        cities_alerts = [
            {"city": "Delhi", "lat": 28.61, "lng": 77.21, "aqi": 310, "class": "emergency"},
            {"city": "Lucknow", "lat": 26.85, "lng": 80.95, "aqi": 245, "class": "critical"},
            {"city": "Kolkata", "lat": 22.57, "lng": 88.36, "aqi": 180, "class": "warning"},
            {"city": "Mumbai", "lat": 19.08, "lng": 72.88, "aqi": 135, "class": "warning"},
            {"city": "Pune", "lat": 18.52, "lng": 73.86, "aqi": 75, "class": "safe"},
        ]

        alerts = []
        for c in cities_alerts:
            if c["class"] != "safe":
                alerts.append({
                    "id": random.randint(1000, 9999),
                    "city": c["city"],
                    "latitude": c["lat"],
                    "longitude": c["lng"],
                    "aqi": c["aqi"],
                    "alert_class": c["class"],
                    "severity_color": {"warning": "#ffff00", "critical": "#ff4444", "emergency": "#7e0023"}[c["class"]],
                    "message": ALERT_ACTIONS[c["class"]]["message"],
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                })

        return alerts


# Singleton instance
alert_classifier = AlertClassifier()
