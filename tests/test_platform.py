"""
Tests for Air Quality Platform API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_data_generator():
    """Test data generation functions."""
    from backend.utils.data_generator import generate_pollutant_data, generate_weather_data, generate_health_records
    from datetime import datetime, timedelta

    # Test pollutant data
    df = generate_pollutant_data(
        start_date=datetime.now() - timedelta(days=7),
        freq_hours=6
    )
    assert len(df) > 0
    assert "pm25" in df.columns
    assert "aqi" in df.columns
    assert df["pm25"].min() >= 0
    assert df["aqi"].min() >= 0

    # Test weather data
    wdf = generate_weather_data(
        start_date=datetime.now() - timedelta(days=7),
        freq_hours=6
    )
    assert len(wdf) > 0
    assert "temperature" in wdf.columns

    # Test health data
    hdf = generate_health_records(50)
    assert len(hdf) == 50
    assert "asthma_risk" in hdf.columns


def test_lstm_forecaster():
    """Test LSTM prediction (simulated mode)."""
    from backend.ml_models.lstm_forecaster import lstm_forecaster

    result = lstm_forecaster.predict(horizon="24h", station_id="DEL001")
    assert "predictions" in result
    assert "timestamps" in result
    assert len(result["predictions"]) == 24
    assert result["model"] == "lstm"


def test_xgboost_health():
    """Test XGBoost health risk prediction."""
    from backend.ml_models.xgboost_health import xgboost_health

    result = xgboost_health.predict({
        "pm25": 120, "pm10": 200, "temperature": 35,
        "humidity": 60, "age": 40, "has_asthma": 1
    })
    assert "risk_scores" in result
    assert "risk_level" in result
    assert "recommendations" in result
    assert result["risk_level"] in ["safe", "low_risk", "moderate_risk", "high_risk", "severe"]


def test_alert_classifier():
    """Test alert classification."""
    from backend.ml_models.alert_classifier import alert_classifier

    result = alert_classifier.classify({"pm25": 200, "pm10": 300, "aqi": 300, "temperature": 40})
    assert "alert_class" in result
    assert result["alert_class"] in ["safe", "warning", "critical", "emergency"]


def test_clustering():
    """Test hotspot detection."""
    from backend.ml_models.clustering import hotspot_detector

    result = hotspot_detector.detect_hotspots()
    assert "clusters" in result


def test_prophet_forecaster():
    """Test Prophet prediction (simulated)."""
    from backend.ml_models.prophet_forecaster import prophet_forecaster

    result = prophet_forecaster.predict(periods=48, station_id="DEL001")
    assert "predictions" in result
    assert "seasonal_components" in result
    assert len(result["predictions"]) == 48


def test_nlp_assistant():
    """Test NLP chatbot."""
    from backend.ml_models.nlp_assistant import nlp_assistant

    result = nlp_assistant.chat("What is AQI?")
    assert "response" in result
    assert len(result["response"]) > 0
    assert "suggestions" in result


def test_recommendation_engine():
    """Test recommendation engine."""
    from backend.ml_models.recommendation_engine import recommendation_engine

    travel = recommendation_engine.get_travel_recommendations(150)
    assert "best_travel_windows" in travel

    outdoor = recommendation_engine.get_outdoor_activities(80, 30, 60)
    assert "safe_activities" in outdoor

    mask = recommendation_engine.get_mask_recommendation(200)
    assert "recommended_mask" in mask


def test_model_manager():
    """Test model manager orchestrator."""
    from backend.ml_models.model_manager import model_manager

    status = model_manager.get_status()
    assert "total_models" in status
    assert status["total_models"] > 0

    result = model_manager.predict_aqi(horizon="24h")
    assert "primary" in result


def test_api_clients():
    """Test API clients with simulated data."""
    from backend.utils.api_clients import OpenWeatherClient, AQICNClient

    weather = OpenWeatherClient()
    result = weather.get_current_weather(28.61, 77.21)
    assert "temperature" in result

    aqicn = AQICNClient()
    result = aqicn.get_station_data(28.61, 77.21)
    assert "aqi" in result


if __name__ == "__main__":
    tests = [
        test_data_generator, test_lstm_forecaster, test_xgboost_health,
        test_alert_classifier, test_clustering, test_prophet_forecaster,
        test_nlp_assistant, test_recommendation_engine, test_model_manager,
        test_api_clients,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
