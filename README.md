# 🌍 Air Quality Forecasting & Smart Health Monitoring Platform

> Enterprise-level AI-powered environmental intelligence system with real-time monitoring, AQI forecasting, health analytics, smart alerting, and geospatial intelligence.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18.3+-blue?logo=react)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.19+-orange?logo=tensorflow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   React UI   │────▶│  Nginx Proxy │────▶│   FastAPI (API)   │
│ Glassmorphism│     │              │     │   Flask (ML)      │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                    │
                     ┌──────────────┐     ┌────────▼─────────┐
                     │  Streamlit   │     │   ML Engine       │
                     │  Analytics   │     │ LSTM│XGBoost│CNN  │
                     └──────────────┘     │ Prophet│SVM│RF    │
                                          └────────┬─────────┘
                                                    │
                            ┌───────────────────────▼────────┐
                            │  SQLite / PostgreSQL  │ Redis  │
                            └────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- pip

### 1. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Start FastAPI server
python -m uvicorn backend.fastapi_services.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Streamlit Dashboard
```bash
streamlit run streamlit_dashboard/app.py
```

### 4. Docker (All services)
```bash
cd docker
docker-compose up --build
```

## 📊 Features

### AI/ML Models (9 Modules)
| # | Module | Algorithm | Purpose |
|---|--------|-----------|---------|
| 1 | AQI Forecasting | LSTM + Attention | 24h/3d/7d/30d predictions |
| 2 | Health Risk | XGBoost | Disease risk scoring with SHAP |
| 3 | Hotspot Detection | K-Means + DBSCAN | Pollution cluster mapping |
| 4 | Alert Classification | SVM + Random Forest | Emergency detection & routing |
| 5 | Satellite Analysis | CNN | Smoke/smog/fire detection |
| 6 | Seasonal Forecast | Prophet + Hybrid | Holiday-aware forecasting |
| 7 | Smart Alerts | Reinforcement Learning | Adaptive threshold optimization |
| 8 | Health Chatbot | NLP + RAG | AI-powered health guidance |
| 9 | Recommendations | Multi-criteria | Travel, masks, routes |

### API Endpoints
| Group | Endpoint | Method |
|-------|----------|--------|
| Auth | `/api/register`, `/api/login` | POST |
| Forecast | `/api/predict-aqi`, `/api/forecast-week` | POST/GET |
| Health | `/api/health-risk`, `/api/disease-probability` | POST/GET |
| Alerts | `/api/send-alert`, `/api/critical-zones` | POST/GET |
| Analytics | `/api/heatmap`, `/api/clusters`, `/api/trends` | GET |
| Chat | `/api/chat` | POST |
| Recommendations | `/api/recommendations/*` | GET |

### Frontend Pages
- **Dashboard** — Real-time AQI gauges, trend charts, city comparison
- **Forecasting** — Multi-model comparison with confidence intervals
- **Health Risk** — Interactive risk assessment with SHAP explainability
- **Alerts** — Severity-coded alert management with routing
- **Analytics** — Correlation matrices, trends, seasonal decomposition

## 🗄️ Database Schema

10 tables: `users`, `pollutants`, `forecasts`, `health_scores`, `alerts`, `clusters`, `hospitals`, `sensor_data`, `weather_data`, `emergency_logs`

## 📓 Jupyter Notebooks

- `notebooks/01_data_cleaning.ipynb` — Data generation, cleaning, feature engineering, EDA

## 🐳 Docker Services

- `fastapi` — Primary API server (port 8000)
- `streamlit` — Analytics dashboard (port 8501)
- `frontend` — React dashboard (port 3000)
- `redis` — Caching layer (port 6379)
- `nginx` — Reverse proxy (port 80)

## 🧪 Testing
```bash
python -m pytest tests/ -v
# or
python tests/test_platform.py
```

## 📁 Project Structure
```
air-quality-platform/
├── backend/
│   ├── fastapi_services/    # FastAPI routes & main app
│   ├── flask_api/           # Flask ML serving
│   ├── auth/                # JWT authentication
│   ├── ml_models/           # 9 AI/ML modules
│   ├── database/            # SQLAlchemy models
│   └── utils/               # Data generators, API clients
├── frontend/                # React + Vite dashboard
├── streamlit_dashboard/     # Streamlit analytics
├── notebooks/               # Jupyter data cleaning
├── datasets/                # Sample data
├── docker/                  # Docker configs
├── deployment/              # Nginx, K8s configs
├── tests/                   # Test suite
└── .github/workflows/       # CI/CD pipeline
```

## 🔑 Environment Variables

See `.env.example` for all configurable settings including:
- API keys (OpenWeather, AQICN, OpenAI)
- Database URL
- JWT secrets
- Feature flags
- Redis configuration

## 📄 License

MIT License — Built for environmental intelligence and public health.
