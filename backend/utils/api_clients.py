"""
Air Quality Platform - External API Clients
Clients for OpenWeather, AQICN, Google Maps with simulated fallbacks.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OpenWeatherClient:
    """OpenWeather API client with simulated fallback."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.use_real = bool(api_key)

    def get_current_weather(self, lat: float, lon: float) -> dict:
        """Get current weather for a location."""
        if self.use_real:
            return self._real_weather(lat, lon)
        return self._simulated_weather(lat, lon)

    def get_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        """Get weather forecast."""
        if self.use_real:
            return self._real_forecast(lat, lon, days)
        return self._simulated_forecast(lat, lon, days)

    def _simulated_weather(self, lat: float, lon: float) -> dict:
        """Generate realistic simulated weather data."""
        now = datetime.now()
        hour = now.hour

        # Temperature based on latitude and time of day
        base_temp = 30 - abs(lat - 23) * 0.5  # Warmer near tropics
        diurnal = 5 * math.sin(2 * math.pi * (hour - 6) / 24)
        temp = base_temp + diurnal + random.gauss(0, 2)

        humidity = max(20, min(98, 60 + random.gauss(0, 15)))
        pressure = 1013 + random.gauss(0, 5)
        wind_speed = max(0.1, random.gauss(3.5, 2))

        conditions = ["Clear", "Clouds", "Haze", "Rain", "Mist"]
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]

        return {
            "temperature": round(temp, 1),
            "feels_like": round(temp + random.uniform(-2, 3), 1),
            "temp_min": round(temp - random.uniform(2, 5), 1),
            "temp_max": round(temp + random.uniform(2, 5), 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": round(random.uniform(0, 360), 0),
            "visibility": round(max(1, 10 - humidity / 20 + random.gauss(0, 1)), 1),
            "cloud_cover": round(max(0, min(100, humidity - 20 + random.gauss(0, 15))), 0),
            "weather_main": random.choices(conditions, weights=weights, k=1)[0],
            "uv_index": round(max(0, 8 * math.sin(math.pi * hour / 12) * (1 - 0.3 * humidity / 100)), 1) if 6 <= hour <= 18 else 0,
            "timestamp": now.isoformat(),
            "source": "simulated",
        }

    def _simulated_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        """Generate simulated weather forecast."""
        forecast = []
        for d in range(days):
            for h in [6, 12, 18, 0]:
                ts = datetime.now() + timedelta(days=d, hours=h - datetime.now().hour)
                base = self._simulated_weather(lat, lon)
                base["timestamp"] = ts.isoformat()
                base["forecast_day"] = d
                forecast.append(base)
        return forecast

    def _real_weather(self, lat: float, lon: float) -> dict:
        """Fetch real weather data from OpenWeather API."""
        try:
            import httpx
            url = f"{self.BASE_URL}/weather"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "visibility": data.get("visibility", 10000) / 1000,
                "cloud_cover": data["clouds"]["all"],
                "weather_main": data["weather"][0]["main"],
                "uv_index": 0,
                "timestamp": datetime.now().isoformat(),
                "source": "openweather",
            }
        except Exception as e:
            logger.warning(f"OpenWeather API failed, using simulation: {e}")
            return self._simulated_weather(lat, lon)

    def _real_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        """Fetch real forecast from OpenWeather API."""
        try:
            import httpx
            url = f"{self.BASE_URL}/forecast"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "wind_speed": item["wind"]["speed"],
                    "weather_main": item["weather"][0]["main"],
                    "timestamp": item["dt_txt"],
                    "source": "openweather",
                }
                for item in data["list"]
            ]
        except Exception as e:
            logger.warning(f"Forecast API failed, using simulation: {e}")
            return self._simulated_forecast(lat, lon, days)


class AQICNClient:
    """AQICN (World Air Quality Index) API client with simulated fallback."""

    BASE_URL = "https://api.waqi.info"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.use_real = bool(api_key)

    def get_station_data(self, lat: float, lon: float) -> dict:
        """Get AQI data for nearest station."""
        if self.use_real:
            return self._real_data(lat, lon)
        return self._simulated_data(lat, lon)

    def _simulated_data(self, lat: float, lon: float) -> dict:
        """Generate simulated AQI station data."""
        now = datetime.now()
        hour = now.hour

        # Base AQI varies by time of day and simulated location
        base_aqi = 80 + random.gauss(0, 30)
        if 7 <= hour <= 10 or 17 <= hour <= 21:
            base_aqi *= 1.3
        elif 2 <= hour <= 5:
            base_aqi *= 0.6

        aqi = max(10, min(400, base_aqi))

        return {
            "aqi": round(aqi),
            "pm25": round(aqi * 0.6 + random.gauss(0, 10), 1),
            "pm10": round(aqi * 1.1 + random.gauss(0, 15), 1),
            "co": round(max(0.1, aqi * 0.015 + random.gauss(0, 0.3)), 2),
            "so2": round(max(1, aqi * 0.1 + random.gauss(0, 3)), 1),
            "no2": round(max(2, aqi * 0.3 + random.gauss(0, 5)), 1),
            "o3": round(max(3, 50 - aqi * 0.1 + random.gauss(0, 8)), 1),
            "temperature": round(25 + random.gauss(0, 5), 1),
            "humidity": round(max(20, min(98, 60 + random.gauss(0, 15))), 1),
            "station": f"Simulated ({lat:.2f}, {lon:.2f})",
            "timestamp": now.isoformat(),
            "source": "simulated",
        }

    def _real_data(self, lat: float, lon: float) -> dict:
        """Fetch real data from AQICN API."""
        try:
            import httpx
            url = f"{self.BASE_URL}/feed/geo:{lat};{lon}/"
            params = {"token": self.api_key}
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "ok":
                d = data["data"]
                iaqi = d.get("iaqi", {})
                return {
                    "aqi": d.get("aqi", 0),
                    "pm25": iaqi.get("pm25", {}).get("v", 0),
                    "pm10": iaqi.get("pm10", {}).get("v", 0),
                    "co": iaqi.get("co", {}).get("v", 0),
                    "so2": iaqi.get("so2", {}).get("v", 0),
                    "no2": iaqi.get("no2", {}).get("v", 0),
                    "o3": iaqi.get("o3", {}).get("v", 0),
                    "temperature": iaqi.get("t", {}).get("v", 0),
                    "humidity": iaqi.get("h", {}).get("v", 0),
                    "station": d.get("city", {}).get("name", "Unknown"),
                    "timestamp": d.get("time", {}).get("iso", ""),
                    "source": "aqicn",
                }
        except Exception as e:
            logger.warning(f"AQICN API failed, using simulation: {e}")
        return self._simulated_data(lat, lon)


class GoogleMapsClient:
    """Google Maps client for geocoding (with fallback)."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def geocode(self, address: str) -> Optional[dict]:
        """Geocode an address to coordinates."""
        # Fallback: known Indian cities
        known = {
            "delhi": (28.6139, 77.2090),
            "mumbai": (19.0760, 72.8777),
            "bangalore": (12.9716, 77.5946),
            "kolkata": (22.5726, 88.3639),
            "chennai": (13.0827, 80.2707),
            "hyderabad": (17.3850, 78.4867),
            "pune": (18.5204, 73.8567),
            "lucknow": (26.8467, 80.9462),
        }

        addr_lower = address.lower()
        for city, (lat, lng) in known.items():
            if city in addr_lower:
                return {"lat": lat, "lng": lng, "formatted": f"{city.title()}, India"}

        # Default to Delhi
        return {"lat": 28.6139, "lng": 77.2090, "formatted": address}


def get_api_clients() -> dict:
    """Create API clients based on available configuration."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config import config

    return {
        "weather": OpenWeatherClient(config.OPENWEATHER_API_KEY),
        "aqicn": AQICNClient(config.AQICN_API_KEY),
        "maps": GoogleMapsClient(config.GOOGLE_MAPS_API_KEY),
    }
