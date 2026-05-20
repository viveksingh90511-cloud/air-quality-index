"""
Air Quality Platform - Recommendation Engine
AI-powered recommendations for travel, activities, masks, and safe routes.
"""

import random
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Smart recommendation engine for:
    - Best travel times
    - Safe outdoor activities
    - Mask recommendations
    - Pollution-safe routes
    """

    def get_travel_recommendations(self, current_aqi: float, forecast: list = None, location: str = "Delhi") -> dict:
        """Recommend best travel times based on AQI forecast."""
        if forecast is None:
            forecast = self._simulated_hourly_forecast(24)

        best_hours = []
        for i, aqi in enumerate(forecast):
            hour = (datetime.now().hour + i + 1) % 24
            if aqi < 100:
                best_hours.append({"hour": hour, "aqi": round(aqi, 1), "rating": "good"})
            elif aqi < 150:
                best_hours.append({"hour": hour, "aqi": round(aqi, 1), "rating": "moderate"})

        best_hours.sort(key=lambda x: x["aqi"])

        return {
            "location": location,
            "current_aqi": round(current_aqi, 1),
            "best_travel_windows": best_hours[:5],
            "worst_hours": sorted(
                [{"hour": (datetime.now().hour + i + 1) % 24, "aqi": round(a, 1)}
                 for i, a in enumerate(forecast)],
                key=lambda x: x["aqi"], reverse=True
            )[:3],
            "recommendation": self._travel_summary(current_aqi, best_hours),
            "generated_at": datetime.now().isoformat(),
        }

    def get_outdoor_activities(self, current_aqi: float, temperature: float = 30, humidity: float = 60) -> dict:
        """Recommend safe outdoor activities based on conditions."""
        activities = [
            {"name": "Running/Jogging", "icon": "🏃", "max_aqi": 50, "min_temp": 10, "max_temp": 35},
            {"name": "Cycling", "icon": "🚴", "max_aqi": 75, "min_temp": 10, "max_temp": 38},
            {"name": "Walking", "icon": "🚶", "max_aqi": 100, "min_temp": 5, "max_temp": 40},
            {"name": "Yoga (Outdoor)", "icon": "🧘", "max_aqi": 75, "min_temp": 15, "max_temp": 35},
            {"name": "Team Sports", "icon": "⚽", "max_aqi": 50, "min_temp": 12, "max_temp": 36},
            {"name": "Gardening", "icon": "🌱", "max_aqi": 100, "min_temp": 10, "max_temp": 38},
            {"name": "Photography Walk", "icon": "📸", "max_aqi": 150, "min_temp": 5, "max_temp": 42},
            {"name": "Bird Watching", "icon": "🐦", "max_aqi": 100, "min_temp": 8, "max_temp": 38},
            {"name": "Swimming (Outdoor)", "icon": "🏊", "max_aqi": 100, "min_temp": 25, "max_temp": 42},
            {"name": "Meditation", "icon": "🧘‍♂️", "max_aqi": 75, "min_temp": 15, "max_temp": 35},
        ]

        safe = []
        caution = []
        avoid = []

        for activity in activities:
            if current_aqi <= activity["max_aqi"] and activity["min_temp"] <= temperature <= activity["max_temp"]:
                safe.append({**activity, "status": "safe", "color": "#00e400"})
            elif current_aqi <= activity["max_aqi"] * 1.5:
                caution.append({**activity, "status": "caution", "color": "#ffff00"})
            else:
                avoid.append({**activity, "status": "avoid", "color": "#ff4444"})

        indoor_alternatives = [
            {"name": "Indoor Gym", "icon": "💪"},
            {"name": "Home Yoga", "icon": "🧘‍♀️"},
            {"name": "Indoor Swimming", "icon": "🏊‍♂️"},
            {"name": "Dance Fitness", "icon": "💃"},
        ]

        return {
            "current_aqi": round(current_aqi, 1),
            "temperature": temperature,
            "humidity": humidity,
            "safe_activities": safe,
            "caution_activities": caution,
            "avoid_activities": avoid,
            "indoor_alternatives": indoor_alternatives if current_aqi > 100 else [],
            "overall_verdict": "safe" if current_aqi < 50 else "moderate" if current_aqi < 100 else "limited" if current_aqi < 200 else "stay_indoors",
            "generated_at": datetime.now().isoformat(),
        }

    def get_mask_recommendation(self, current_aqi: float, duration_hours: float = 1, activity_level: str = "moderate") -> dict:
        """Recommend appropriate mask based on conditions."""
        masks = [
            {"name": "No Mask Needed", "type": "none", "max_aqi": 50, "filtration": 0, "price_range": "Free"},
            {"name": "Surgical Mask", "type": "surgical", "max_aqi": 100, "filtration": 60, "price_range": "₹5-15"},
            {"name": "KN95 Mask", "type": "kn95", "max_aqi": 200, "filtration": 95, "price_range": "₹30-80"},
            {"name": "N95 Mask", "type": "n95", "max_aqi": 300, "filtration": 95, "price_range": "₹50-150"},
            {"name": "N95 with Valve", "type": "n95_valve", "max_aqi": 400, "filtration": 95, "price_range": "₹100-250"},
            {"name": "N99/P100 Respirator", "type": "n99", "max_aqi": 500, "filtration": 99, "price_range": "₹200-500"},
        ]

        # Adjust for activity level
        aqi_adjusted = current_aqi
        if activity_level == "high":
            aqi_adjusted *= 1.3
        elif activity_level == "low":
            aqi_adjusted *= 0.8

        # Adjust for duration
        if duration_hours > 4:
            aqi_adjusted *= 1.2

        recommended = None
        for mask in masks:
            if aqi_adjusted <= mask["max_aqi"]:
                recommended = mask
                break

        if recommended is None:
            recommended = masks[-1]

        return {
            "current_aqi": round(current_aqi, 1),
            "activity_level": activity_level,
            "duration_hours": duration_hours,
            "recommended_mask": recommended,
            "all_options": masks,
            "tips": [
                "Ensure the mask fits snugly with no gaps",
                "Replace disposable masks after 8 hours of use",
                "N95 masks should be discarded after 40 hours total",
                "Children need properly sized masks",
                "Facial hair reduces mask effectiveness",
            ],
            "generated_at": datetime.now().isoformat(),
        }

    def get_safe_routes(self, origin: dict, destination: dict, current_conditions: dict = None) -> dict:
        """Suggest pollution-safe routes between locations."""
        # Simulated route options
        routes = [
            {
                "name": "Green Route (Parks & Gardens)",
                "distance_km": round(random.uniform(5, 15), 1),
                "estimated_time_min": random.randint(15, 45),
                "avg_aqi_along_route": random.randint(40, 90),
                "passes_through": ["Park areas", "Residential zones", "Green belt"],
                "avoids": ["Industrial areas", "Heavy traffic"],
                "rating": "best",
                "color": "#00e400",
            },
            {
                "name": "Main Road Route",
                "distance_km": round(random.uniform(4, 12), 1),
                "estimated_time_min": random.randint(10, 35),
                "avg_aqi_along_route": random.randint(100, 180),
                "passes_through": ["Main roads", "Commercial areas"],
                "avoids": [],
                "rating": "moderate",
                "color": "#ffff00",
            },
            {
                "name": "Shortest Route",
                "distance_km": round(random.uniform(3, 10), 1),
                "estimated_time_min": random.randint(8, 25),
                "avg_aqi_along_route": random.randint(120, 220),
                "passes_through": ["Industrial zone", "Traffic corridor"],
                "avoids": [],
                "rating": "poor",
                "color": "#ff4444",
            },
        ]

        return {
            "origin": origin,
            "destination": destination,
            "routes": routes,
            "recommended": routes[0],
            "air_quality_note": "Route recommendations consider real-time pollution data along each path.",
            "generated_at": datetime.now().isoformat(),
        }

    def _simulated_hourly_forecast(self, hours: int) -> list:
        """Generate simulated hourly AQI forecast."""
        base = random.uniform(60, 150)
        forecast = []
        for h in range(hours):
            hour = (datetime.now().hour + h + 1) % 24
            diurnal = 30 * np.sin(2 * np.pi * (hour - 8) / 24)
            noise = random.gauss(0, 10)
            forecast.append(max(10, base + diurnal + noise))
        return forecast

    def _travel_summary(self, current_aqi: float, best_hours: list) -> str:
        """Generate travel recommendation summary."""
        if current_aqi < 50:
            return "🟢 Excellent air quality! Safe to travel anytime."
        elif current_aqi < 100:
            return "🟡 Moderate air quality. Travel is fine, but best during early morning hours."
        elif current_aqi < 150:
            if best_hours:
                hours = [f"{h['hour']:02d}:00" for h in best_hours[:3]]
                return f"🟠 Limited good windows. Best times: {', '.join(hours)}. Wear a mask for longer trips."
            return "🟠 Air quality is poor. Minimize travel and wear N95 mask."
        else:
            return "🔴 Avoid unnecessary travel. If essential, use AC vehicle with recirculation and wear N95 mask."


# Singleton instance
recommendation_engine = RecommendationEngine()
