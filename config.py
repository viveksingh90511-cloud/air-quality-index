"""
Air Quality Platform - Centralized Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration."""

    # Application
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-key-change-me")
    APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'air_quality.db'}")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 300))

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-change-me")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # External APIs
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    AQICN_API_KEY = os.getenv("AQICN_API_KEY", "")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # AI/LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "simulated")

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # ML Models
    MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", str(BASE_DIR / "ml_model_cache")))
    MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

    # Feature Flags
    ENABLE_CNN_SATELLITE = os.getenv("ENABLE_CNN_SATELLITE", "false").lower() == "true"
    ENABLE_CROWD_DETECTION = os.getenv("ENABLE_CROWD_DETECTION", "false").lower() == "true"
    ENABLE_BLOCKCHAIN_LOGS = os.getenv("ENABLE_BLOCKCHAIN_LOGS", "false").lower() == "true"
    ENABLE_REAL_APIS = os.getenv("ENABLE_REAL_APIS", "false").lower() == "true"

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))

    # AQI Categories
    AQI_CATEGORIES = {
        (0, 50): {"label": "Good", "color": "#00e400", "health": "Air quality is satisfactory."},
        (51, 100): {"label": "Moderate", "color": "#ffff00", "health": "Acceptable air quality."},
        (101, 150): {"label": "Unhealthy for Sensitive", "color": "#ff7e00", "health": "Sensitive groups may experience effects."},
        (151, 200): {"label": "Unhealthy", "color": "#ff0000", "health": "Everyone may experience health effects."},
        (201, 300): {"label": "Very Unhealthy", "color": "#8f3f97", "health": "Health alert: serious effects."},
        (301, 500): {"label": "Hazardous", "color": "#7e0023", "health": "Emergency conditions."},
    }

    @classmethod
    def get_aqi_category(cls, aqi_value: float) -> dict:
        """Get AQI category info for a given AQI value."""
        for (low, high), info in cls.AQI_CATEGORIES.items():
            if low <= aqi_value <= high:
                return info
        return {"label": "Beyond Index", "color": "#7e0023", "health": "Extremely hazardous."}

    @classmethod
    def is_production(cls) -> bool:
        return cls.APP_ENV == "production"

    @classmethod
    def has_api_key(cls, service: str) -> bool:
        """Check if an API key is configured for a service."""
        key_map = {
            "openweather": cls.OPENWEATHER_API_KEY,
            "aqicn": cls.AQICN_API_KEY,
            "google_maps": cls.GOOGLE_MAPS_API_KEY,
            "openai": cls.OPENAI_API_KEY,
            "gemini": cls.GEMINI_API_KEY,
        }
        return bool(key_map.get(service, ""))


config = Config()
