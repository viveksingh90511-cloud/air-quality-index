"""
Air Quality Platform - SQLAlchemy ORM Models
All database tables for the enterprise platform.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """Base model class."""
    pass


# ===================== ENUMS =====================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"


class AlertSeverity(str, enum.Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    LOW = "low_risk"
    MODERATE = "moderate_risk"
    HIGH = "high_risk"
    SEVERE = "severe"


class SensorStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


# ===================== MODELS =====================

class User(Base):
    """User accounts with role-based access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    full_name = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    profile = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    health_scores = relationship("HealthScore", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Pollutant(Base):
    """Real-time pollutant readings from monitoring stations."""
    __tablename__ = "pollutants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False, index=True)
    station_name = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String(100), nullable=True)
    country = Column(String(80), nullable=True, default="India")

    # Pollutant concentrations (µg/m³)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    no2 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)

    # Computed AQI
    aqi = Column(Float, nullable=True)
    dominant_pollutant = Column(String(10), nullable=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_pollutant_station_time", "station_id", "timestamp"),
        Index("idx_pollutant_location", "latitude", "longitude"),
    )

    def __repr__(self):
        return f"<Pollutant(station='{self.station_id}', aqi={self.aqi}, ts='{self.timestamp}')>"


class Forecast(Base):
    """AQI forecast predictions from ML models."""
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # lstm, prophet, xgboost, ensemble
    predicted_aqi = Column(Float, nullable=False)
    actual_aqi = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    horizon = Column(String(20), nullable=False)  # 24h, 3d, 7d, 30d
    prediction_details = Column(JSON, default=dict)
    forecast_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Accuracy metrics (filled after actual data arrives)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_forecast_station_date", "station_id", "forecast_date"),
        Index("idx_forecast_model", "model_type"),
    )

    def __repr__(self):
        return f"<Forecast(model='{self.model_type}', aqi={self.predicted_aqi}, horizon='{self.horizon}')>"


class HealthScore(Base):
    """Health risk assessments for users based on environmental conditions."""
    __tablename__ = "health_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    location = Column(String(150), nullable=True)
    current_aqi = Column(Float, nullable=True)

    # Risk scores (0.0 - 1.0)
    asthma_risk = Column(Float, nullable=True)
    respiratory_risk = Column(Float, nullable=True)
    cardiovascular_risk = Column(Float, nullable=True)
    heatstroke_risk = Column(Float, nullable=True)
    elderly_vulnerability = Column(Float, nullable=True)
    child_sensitivity = Column(Float, nullable=True)

    # Overall
    overall_risk = Column(SQLEnum(RiskLevel), default=RiskLevel.SAFE)
    overall_score = Column(Float, nullable=True)
    recommendations = Column(JSON, default=list)
    shap_values = Column(JSON, default=dict)

    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="health_scores")

    def __repr__(self):
        return f"<HealthScore(user={self.user_id}, risk='{self.overall_risk}', score={self.overall_score})>"


class Alert(Base):
    """Environmental emergency alerts."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # aqi, weather, toxic_gas, fire
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    zone_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    station_id = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    affected_population = Column(Integer, nullable=True)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    auto_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    zone = relationship("Cluster", back_populates="alerts")
    emergency_logs = relationship("EmergencyLog", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Alert(severity='{self.severity}', type='{self.alert_type}', status='{self.status}')>"


class Cluster(Base):
    """Spatial clusters for pollution hotspots."""
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_type = Column(String(50), nullable=False)  # pollution, industrial, traffic, urban_risk
    algorithm = Column(String(30), nullable=False, default="kmeans")  # kmeans, dbscan
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=True)
    num_points = Column(Integer, nullable=True)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MODERATE)
    avg_aqi = Column(Float, nullable=True)
    cluster_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="zone")

    def __repr__(self):
        return f"<Cluster(type='{self.cluster_type}', risk='{self.risk_level}', center=({self.centroid_lat},{self.centroid_lng}))>"


class Hospital(Base):
    """Hospital and emergency response facilities."""
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    hospital_type = Column(String(50), default="general")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(300), nullable=True)
    city = Column(String(100), nullable=True)
    capacity = Column(Integer, nullable=True)
    available_beds = Column(Integer, nullable=True)
    specialization = Column(String(100), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    alert_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    emergency_logs = relationship("EmergencyLog", back_populates="hospital")

    def __repr__(self):
        return f"<Hospital(name='{self.name}', city='{self.city}')>"


class SensorData(Base):
    """IoT sensor telemetry data."""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=True)  # air_quality, weather, traffic
    station_id = Column(String(50), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    readings = Column(JSON, nullable=False, default=dict)
    battery_level = Column(Float, nullable=True)
    signal_strength = Column(Float, nullable=True)
    status = Column(SQLEnum(SensorStatus), default=SensorStatus.ONLINE)
    firmware_version = Column(String(20), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_sensor_time", "sensor_id", "timestamp"),
    )

    def __repr__(self):
        return f"<SensorData(sensor='{self.sensor_id}', status='{self.status}')>"


class WeatherData(Base):
    """Weather observation data."""
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(150), nullable=False, index=True)
    station_id = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)       # °C
    humidity = Column(Float, nullable=True)           # %
    pressure = Column(Float, nullable=True)           # hPa
    wind_speed = Column(Float, nullable=True)         # m/s
    wind_direction = Column(Float, nullable=True)     # degrees
    visibility = Column(Float, nullable=True)         # km
    precipitation = Column(Float, nullable=True)      # mm
    uv_index = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)        # %
    weather_condition = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_weather_loc_time", "location", "timestamp"),
    )

    def __repr__(self):
        return f"<WeatherData(location='{self.location}', temp={self.temperature}°C)>"


class EmergencyLog(Base):
    """Logs of emergency response actions."""
    __tablename__ = "emergency_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    action_taken = Column(String(200), nullable=False)
    responder = Column(String(150), nullable=True)
    response_time_minutes = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    resolution = Column(String(200), nullable=True)
    status = Column(String(50), default="pending")
    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    alert = relationship("Alert", back_populates="emergency_logs")
    hospital = relationship("Hospital", back_populates="emergency_logs")

    def __repr__(self):
        return f"<EmergencyLog(alert={self.alert_id}, action='{self.action_taken}')>"
