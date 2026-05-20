"""
Air Quality Platform - Realistic Data Generator
Generates synthetic but realistic environmental monitoring data with
seasonal patterns, correlations, and anomalies.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import json

# ===================== INDIAN CITIES MONITORING STATIONS =====================

STATIONS = [
    {"id": "DEL001", "name": "Delhi - Anand Vihar", "city": "Delhi", "lat": 28.6508, "lng": 77.3152},
    {"id": "DEL002", "name": "Delhi - ITO", "city": "Delhi", "lat": 28.6289, "lng": 77.2411},
    {"id": "MUM001", "name": "Mumbai - Bandra", "city": "Mumbai", "lat": 19.0544, "lng": 72.8404},
    {"id": "MUM002", "name": "Mumbai - Worli", "city": "Mumbai", "lat": 19.0176, "lng": 72.8152},
    {"id": "BLR001", "name": "Bangalore - Koramangala", "city": "Bangalore", "lat": 12.9352, "lng": 77.6245},
    {"id": "KOL001", "name": "Kolkata - Jadavpur", "city": "Kolkata", "lat": 22.4990, "lng": 88.3714},
    {"id": "CHN001", "name": "Chennai - T. Nagar", "city": "Chennai", "lat": 13.0418, "lng": 80.2341},
    {"id": "HYD001", "name": "Hyderabad - Jubilee Hills", "city": "Hyderabad", "lat": 17.4326, "lng": 78.4071},
    {"id": "PUN001", "name": "Pune - Shivajinagar", "city": "Pune", "lat": 18.5308, "lng": 73.8475},
    {"id": "LKN001", "name": "Lucknow - Gomti Nagar", "city": "Lucknow", "lat": 26.8563, "lng": 80.9918},
]

# Base pollution profiles per city (annual average)
CITY_PROFILES = {
    "Delhi": {"pm25": 120, "pm10": 200, "co": 2.5, "so2": 18, "no2": 55, "o3": 35, "volatility": 1.4},
    "Mumbai": {"pm25": 65, "pm10": 110, "co": 1.8, "so2": 12, "no2": 40, "o3": 30, "volatility": 1.0},
    "Bangalore": {"pm25": 45, "pm10": 80, "co": 1.2, "so2": 8, "no2": 30, "o3": 28, "volatility": 0.8},
    "Kolkata": {"pm25": 80, "pm10": 140, "co": 2.0, "so2": 15, "no2": 45, "o3": 32, "volatility": 1.1},
    "Chennai": {"pm25": 40, "pm10": 75, "co": 1.0, "so2": 7, "no2": 25, "o3": 25, "volatility": 0.7},
    "Hyderabad": {"pm25": 55, "pm10": 95, "co": 1.5, "so2": 10, "no2": 35, "o3": 30, "volatility": 0.9},
    "Pune": {"pm25": 50, "pm10": 85, "co": 1.3, "so2": 9, "no2": 32, "o3": 27, "volatility": 0.85},
    "Lucknow": {"pm25": 100, "pm10": 170, "co": 2.2, "so2": 16, "no2": 50, "o3": 33, "volatility": 1.3},
}


def _seasonal_factor(timestamp: datetime) -> float:
    """Winter pollution spike (Oct-Feb), monsoon dip (Jun-Sep)."""
    month = timestamp.month
    if month in [11, 12, 1]:
        return 1.6 + random.uniform(-0.1, 0.2)  # Winter peak
    elif month in [2, 10]:
        return 1.3 + random.uniform(-0.1, 0.1)
    elif month in [6, 7, 8]:
        return 0.5 + random.uniform(-0.05, 0.1)  # Monsoon low
    elif month == 9:
        return 0.7 + random.uniform(-0.05, 0.1)
    else:
        return 1.0 + random.uniform(-0.1, 0.1)


def _diurnal_factor(hour: int) -> float:
    """Daily pollution pattern: peaks at 8-10 AM and 6-9 PM (traffic hours)."""
    if 7 <= hour <= 10:
        return 1.3 + random.uniform(-0.05, 0.1)
    elif 17 <= hour <= 21:
        return 1.4 + random.uniform(-0.05, 0.15)
    elif 2 <= hour <= 5:
        return 0.6 + random.uniform(-0.05, 0.05)
    else:
        return 1.0 + random.uniform(-0.1, 0.1)


def _weekend_factor(timestamp: datetime) -> float:
    """Weekends have slightly lower pollution due to less traffic."""
    if timestamp.weekday() >= 5:
        return 0.85 + random.uniform(-0.05, 0.05)
    return 1.0


def calculate_aqi(pm25: float, pm10: float, co: float, so2: float, no2: float, o3: float) -> tuple:
    """Calculate AQI using Indian NAQI breakpoints (simplified)."""
    sub_indices = {}

    # PM2.5 breakpoints
    if pm25 <= 30: sub_indices["PM2.5"] = pm25 * 50 / 30
    elif pm25 <= 60: sub_indices["PM2.5"] = 50 + (pm25 - 30) * 50 / 30
    elif pm25 <= 90: sub_indices["PM2.5"] = 100 + (pm25 - 60) * 100 / 30
    elif pm25 <= 120: sub_indices["PM2.5"] = 200 + (pm25 - 90) * 100 / 30
    elif pm25 <= 250: sub_indices["PM2.5"] = 300 + (pm25 - 120) * 100 / 130
    else: sub_indices["PM2.5"] = 400 + (pm25 - 250) * 100 / 130

    # PM10 breakpoints
    if pm10 <= 50: sub_indices["PM10"] = pm10
    elif pm10 <= 100: sub_indices["PM10"] = 50 + (pm10 - 50)
    elif pm10 <= 250: sub_indices["PM10"] = 100 + (pm10 - 100) * 100 / 150
    elif pm10 <= 350: sub_indices["PM10"] = 200 + (pm10 - 250) * 100 / 100
    elif pm10 <= 430: sub_indices["PM10"] = 300 + (pm10 - 350) * 100 / 80
    else: sub_indices["PM10"] = 400 + (pm10 - 430) * 100 / 80

    # Simplified sub-indices for other pollutants
    sub_indices["CO"] = min(co * 50, 500)
    sub_indices["SO2"] = min(so2 * 2.5, 500)
    sub_indices["NO2"] = min(no2 * 2, 500)
    sub_indices["O3"] = min(o3 * 2.5, 500)

    aqi = max(sub_indices.values())
    dominant = max(sub_indices, key=sub_indices.get)
    return round(aqi, 1), dominant


def generate_pollutant_data(
    start_date: datetime = None,
    end_date: datetime = None,
    stations: list = None,
    freq_hours: int = 1
) -> pd.DataFrame:
    """
    Generate realistic hourly pollutant data for monitoring stations.

    Args:
        start_date: Start datetime (default: 1 year ago)
        end_date: End datetime (default: now)
        stations: List of station dicts (default: STATIONS)
        freq_hours: Frequency in hours (default: 1)

    Returns:
        DataFrame with pollutant readings
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    if stations is None:
        stations = STATIONS

    records = []
    timestamps = pd.date_range(start=start_date, end=end_date, freq=f"{freq_hours}h")

    for station in stations:
        profile = CITY_PROFILES.get(station["city"], CITY_PROFILES["Pune"])
        volatility = profile["volatility"]

        # Generate correlated noise for realistic data
        n = len(timestamps)
        noise_pm25 = np.cumsum(np.random.randn(n) * 0.3) * volatility
        noise_pm10 = noise_pm25 * 1.5 + np.cumsum(np.random.randn(n) * 0.2)

        for i, ts in enumerate(timestamps):
            ts_dt = ts.to_pydatetime()
            sf = _seasonal_factor(ts_dt)
            df = _diurnal_factor(ts_dt.hour)
            wf = _weekend_factor(ts_dt)
            combined = sf * df * wf

            # Add Diwali spike (late October/early November)
            diwali_spike = 1.0
            if ts_dt.month == 10 and ts_dt.day >= 25:
                diwali_spike = 2.5
            elif ts_dt.month == 11 and ts_dt.day <= 5:
                diwali_spike = 2.0 - (ts_dt.day - 1) * 0.2

            combined *= diwali_spike

            pm25 = max(5, profile["pm25"] * combined + noise_pm25[i] * 10)
            pm10 = max(10, profile["pm10"] * combined + noise_pm10[i] * 12)
            co = max(0.1, profile["co"] * combined * random.uniform(0.7, 1.3))
            so2 = max(1, profile["so2"] * combined * random.uniform(0.6, 1.4))
            no2 = max(2, profile["no2"] * combined * random.uniform(0.7, 1.3))
            o3 = max(3, profile["o3"] * (2.0 - combined * 0.5) * random.uniform(0.7, 1.3))

            aqi, dominant = calculate_aqi(pm25, pm10, co, so2, no2, o3)

            records.append({
                "station_id": station["id"],
                "station_name": station["name"],
                "city": station["city"],
                "latitude": station["lat"],
                "longitude": station["lng"],
                "pm25": round(pm25, 2),
                "pm10": round(pm10, 2),
                "co": round(co, 2),
                "so2": round(so2, 2),
                "no2": round(no2, 2),
                "o3": round(o3, 2),
                "aqi": aqi,
                "dominant_pollutant": dominant,
                "timestamp": ts_dt,
            })

    df = pd.DataFrame(records)
    return df


def generate_weather_data(
    start_date: datetime = None,
    end_date: datetime = None,
    stations: list = None,
    freq_hours: int = 1
) -> pd.DataFrame:
    """Generate realistic weather data correlated with Indian climate patterns."""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    if stations is None:
        stations = STATIONS

    CITY_CLIMATE = {
        "Delhi": {"temp_base": 25, "temp_amp": 15, "humidity_base": 55, "rain_months": [7, 8, 9]},
        "Mumbai": {"temp_base": 28, "temp_amp": 5, "humidity_base": 75, "rain_months": [6, 7, 8, 9]},
        "Bangalore": {"temp_base": 24, "temp_amp": 5, "humidity_base": 60, "rain_months": [6, 7, 8, 9, 10]},
        "Kolkata": {"temp_base": 27, "temp_amp": 10, "humidity_base": 70, "rain_months": [6, 7, 8, 9]},
        "Chennai": {"temp_base": 29, "temp_amp": 5, "humidity_base": 70, "rain_months": [10, 11, 12]},
        "Hyderabad": {"temp_base": 27, "temp_amp": 8, "humidity_base": 55, "rain_months": [6, 7, 8, 9]},
        "Pune": {"temp_base": 26, "temp_amp": 8, "humidity_base": 55, "rain_months": [6, 7, 8, 9]},
        "Lucknow": {"temp_base": 26, "temp_amp": 14, "humidity_base": 60, "rain_months": [7, 8, 9]},
    }

    records = []
    timestamps = pd.date_range(start=start_date, end=end_date, freq=f"{freq_hours}h")

    for station in stations:
        climate = CITY_CLIMATE.get(station["city"], CITY_CLIMATE["Pune"])

        for ts in timestamps:
            ts_dt = ts.to_pydatetime()
            day_of_year = ts_dt.timetuple().tm_yday

            # Temperature: seasonal + diurnal
            seasonal_temp = climate["temp_base"] + climate["temp_amp"] * np.sin(
                2 * np.pi * (day_of_year - 120) / 365
            )
            diurnal_temp = 5 * np.sin(2 * np.pi * (ts_dt.hour - 6) / 24)
            temp = seasonal_temp + diurnal_temp + random.gauss(0, 1.5)

            # Humidity
            is_rain_month = ts_dt.month in climate["rain_months"]
            base_humidity = climate["humidity_base"] + (20 if is_rain_month else 0)
            humidity = min(98, max(20, base_humidity + random.gauss(0, 10) - diurnal_temp * 2))

            # Pressure
            pressure = 1013 + random.gauss(0, 5) - (0.1 * temp)

            # Wind
            wind_speed = max(0.1, random.gauss(3, 2) + (2 if 12 <= ts_dt.hour <= 16 else 0))
            wind_direction = random.uniform(0, 360)

            # Precipitation
            precipitation = 0.0
            if is_rain_month and random.random() < 0.3:
                precipitation = random.expovariate(0.3)

            # Visibility
            visibility = max(0.5, 10 - (humidity / 20) + random.gauss(0, 1))

            conditions = ["Clear", "Partly Cloudy", "Cloudy", "Haze", "Rain", "Thunderstorm", "Fog"]
            if precipitation > 5:
                condition = "Thunderstorm"
            elif precipitation > 0:
                condition = "Rain"
            elif humidity > 85:
                condition = "Fog" if ts_dt.hour < 8 else "Haze"
            elif humidity > 60:
                condition = random.choice(["Partly Cloudy", "Cloudy", "Haze"])
            else:
                condition = random.choice(["Clear", "Partly Cloudy"])

            records.append({
                "location": station["city"],
                "station_id": station["id"],
                "latitude": station["lat"],
                "longitude": station["lng"],
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "pressure": round(pressure, 1),
                "wind_speed": round(wind_speed, 1),
                "wind_direction": round(wind_direction, 1),
                "visibility": round(visibility, 1),
                "precipitation": round(precipitation, 2),
                "uv_index": round(max(0, 8 * np.sin(np.pi * ts_dt.hour / 12) * (1 - 0.3 * (humidity / 100))), 1) if 6 <= ts_dt.hour <= 18 else 0,
                "cloud_cover": round(min(100, max(0, humidity - 20 + random.gauss(0, 15))), 0),
                "weather_condition": condition,
                "timestamp": ts_dt,
            })

    return pd.DataFrame(records)


def generate_sensor_data(num_sensors: int = 20, hours: int = 168) -> pd.DataFrame:
    """Generate IoT sensor telemetry data."""
    records = []
    now = datetime.now()

    for i in range(num_sensors):
        sensor_id = f"SENSOR_{i+1:03d}"
        sensor_type = random.choice(["air_quality", "weather", "traffic", "industrial"])
        station = random.choice(STATIONS)
        lat = station["lat"] + random.uniform(-0.05, 0.05)
        lng = station["lng"] + random.uniform(-0.05, 0.05)
        battery = 100.0

        for h in range(hours):
            ts = now - timedelta(hours=hours - h)
            battery = max(5, battery - random.uniform(0, 0.15))
            status = "online"
            if battery < 15:
                status = random.choice(["online", "offline"])
            if random.random() < 0.02:
                status = "error"

            readings = {}
            if sensor_type == "air_quality":
                readings = {
                    "pm25": round(random.uniform(10, 200), 1),
                    "pm10": round(random.uniform(20, 350), 1),
                    "co": round(random.uniform(0.1, 5), 2),
                    "voc": round(random.uniform(0, 500), 0),
                }
            elif sensor_type == "weather":
                readings = {
                    "temperature": round(random.uniform(15, 45), 1),
                    "humidity": round(random.uniform(20, 95), 1),
                    "pressure": round(random.uniform(990, 1030), 1),
                }
            elif sensor_type == "traffic":
                hour_factor = 1.5 if 8 <= ts.hour <= 10 or 17 <= ts.hour <= 20 else 0.7
                readings = {
                    "vehicle_count": int(random.uniform(50, 500) * hour_factor),
                    "avg_speed_kmh": round(random.uniform(10, 60) / hour_factor, 1),
                    "congestion_level": round(min(1.0, random.uniform(0.2, 0.8) * hour_factor), 2),
                }
            elif sensor_type == "industrial":
                readings = {
                    "emission_rate": round(random.uniform(10, 100), 1),
                    "stack_temperature": round(random.uniform(100, 300), 0),
                    "opacity": round(random.uniform(0, 40), 1),
                }

            records.append({
                "sensor_id": sensor_id,
                "sensor_type": sensor_type,
                "station_id": station["id"],
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
                "readings": readings,
                "battery_level": round(battery, 1),
                "signal_strength": round(random.uniform(-90, -30), 1),
                "status": status,
                "firmware_version": "2.1.3",
                "timestamp": ts,
            })

    return pd.DataFrame(records)


def generate_health_records(num_records: int = 500) -> pd.DataFrame:
    """Generate health risk assessment records."""
    records = []
    cities = list(CITY_PROFILES.keys())

    for i in range(num_records):
        city = random.choice(cities)
        profile = CITY_PROFILES[city]
        base_aqi = profile["pm25"] * 1.5

        aqi = max(10, base_aqi * random.uniform(0.3, 2.0))
        temp = random.uniform(15, 45)
        humidity = random.uniform(20, 95)

        # Risk calculations correlated with AQI
        aqi_factor = min(aqi / 300, 1.0)
        heat_factor = max(0, (temp - 35) / 15)

        asthma = min(1.0, aqi_factor * 0.8 + random.uniform(0, 0.2))
        respiratory = min(1.0, aqi_factor * 0.7 + random.uniform(0, 0.15))
        cardio = min(1.0, aqi_factor * 0.5 + heat_factor * 0.3 + random.uniform(0, 0.1))
        heatstroke = min(1.0, heat_factor * 0.7 + (1 - humidity / 100) * 0.2 + random.uniform(0, 0.1))
        elderly = min(1.0, (asthma + cardio + heatstroke) / 2.5 + random.uniform(0, 0.1))
        child = min(1.0, (asthma + respiratory) / 1.8 + random.uniform(0, 0.1))

        overall = (asthma * 0.25 + respiratory * 0.25 + cardio * 0.2 +
                   heatstroke * 0.1 + elderly * 0.1 + child * 0.1)

        if overall < 0.2: risk = "safe"
        elif overall < 0.4: risk = "low_risk"
        elif overall < 0.6: risk = "moderate_risk"
        elif overall < 0.8: risk = "high_risk"
        else: risk = "severe"

        records.append({
            "location": city,
            "current_aqi": round(aqi, 1),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "asthma_risk": round(asthma, 4),
            "respiratory_risk": round(respiratory, 4),
            "cardiovascular_risk": round(cardio, 4),
            "heatstroke_risk": round(heatstroke, 4),
            "elderly_vulnerability": round(elderly, 4),
            "child_sensitivity": round(child, 4),
            "overall_risk": risk,
            "overall_score": round(overall, 4),
            "timestamp": datetime.now() - timedelta(hours=random.randint(0, 8760)),
        })

    return pd.DataFrame(records)


def generate_hospital_data() -> pd.DataFrame:
    """Generate hospital/emergency facility data."""
    hospitals = [
        {"name": "AIIMS Delhi", "city": "Delhi", "lat": 28.5672, "lng": 77.2100, "capacity": 2500, "spec": "Multi-specialty"},
        {"name": "Safdarjung Hospital", "city": "Delhi", "lat": 28.5685, "lng": 77.2066, "capacity": 1800, "spec": "General"},
        {"name": "Sir Ganga Ram Hospital", "city": "Delhi", "lat": 28.6362, "lng": 77.1885, "capacity": 800, "spec": "Pulmonology"},
        {"name": "Lilavati Hospital", "city": "Mumbai", "lat": 19.0509, "lng": 72.8289, "capacity": 600, "spec": "Cardiology"},
        {"name": "KEM Hospital", "city": "Mumbai", "lat": 19.0019, "lng": 72.8425, "capacity": 1800, "spec": "General"},
        {"name": "Manipal Hospital", "city": "Bangalore", "lat": 12.9591, "lng": 77.6488, "capacity": 700, "spec": "Multi-specialty"},
        {"name": "Apollo Hospital Chennai", "city": "Chennai", "lat": 13.0067, "lng": 80.2206, "capacity": 600, "spec": "Respiratory"},
        {"name": "KGMU Hospital", "city": "Lucknow", "lat": 26.8567, "lng": 80.9419, "capacity": 1000, "spec": "General"},
        {"name": "SSKM Hospital", "city": "Kolkata", "lat": 22.5354, "lng": 88.3444, "capacity": 1500, "spec": "Multi-specialty"},
        {"name": "Nizam's Institute", "city": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "capacity": 800, "spec": "Cardiology"},
        {"name": "Sassoon Hospital", "city": "Pune", "lat": 18.5283, "lng": 73.8746, "capacity": 1200, "spec": "General"},
        {"name": "Ruby Hall Clinic", "city": "Pune", "lat": 18.5315, "lng": 73.8853, "capacity": 550, "spec": "Pulmonology"},
    ]

    records = []
    for h in hospitals:
        records.append({
            "name": h["name"],
            "hospital_type": "government" if "AIIMS" in h["name"] or "KEM" in h["name"] or "KGMU" in h["name"] or "SSKM" in h["name"] or "Sassoon" in h["name"] else "private",
            "latitude": h["lat"],
            "longitude": h["lng"],
            "address": f"{h['name']}, {h['city']}",
            "city": h["city"],
            "capacity": h["capacity"],
            "available_beds": int(h["capacity"] * random.uniform(0.1, 0.4)),
            "specialization": h["spec"],
            "emergency_contact": f"+91-{random.randint(1000000000, 9999999999)}",
            "alert_enabled": True,
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    print("Generating sample data...")
    pollutants = generate_pollutant_data(freq_hours=6)
    print(f"  Pollutants: {len(pollutants)} records")

    weather = generate_weather_data(freq_hours=6)
    print(f"  Weather: {len(weather)} records")

    sensors = generate_sensor_data(num_sensors=10, hours=48)
    print(f"  Sensors: {len(sensors)} records")

    health = generate_health_records(200)
    print(f"  Health: {len(health)} records")

    hospitals = generate_hospital_data()
    print(f"  Hospitals: {len(hospitals)} records")

    print("\nSample pollutant record:")
    print(pollutants.iloc[0].to_dict())
