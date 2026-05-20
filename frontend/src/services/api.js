/**
 * Air Quality Platform - Axios API Client Layer
 * Centralized HTTP client with interceptors, error handling, and typed helpers.
 */

import axios from 'axios'

// ─────────────────────────── BASE CLIENT ──────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle errors globally
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    const message = error.response?.data?.detail || error.response?.data?.error || error.message || 'Unknown error'
    console.error(`[API Error] ${error.config?.url}: ${message}`)
    return Promise.reject(new Error(message))
  }
)

// ─────────────────────────── AUTH ─────────────────────────────────

export const authAPI = {
  register: (data) => api.post('/api/register', data),
  login: (data) => api.post('/api/login', data),
  logout: (token) => api.post('/api/logout', { token }),
  me: () => api.get('/api/me'),
}

// ─────────────────────────── FORECAST ─────────────────────────────

export const forecastAPI = {
  /** @param {string} stationId @param {string} horizon — '24h'|'3d'|'7d'|'30d' */
  predict: (stationId = 'DEL001', horizon = '24h') =>
    api.post('/api/predict-aqi', null, { params: { station_id: stationId, horizon } }),

  week: (stationId = 'DEL001') =>
    api.get('/api/forecast-week', { params: { station_id: stationId } }),

  month: (stationId = 'DEL001') =>
    api.get('/api/forecast-month', { params: { station_id: stationId } }),

  compare: (stationId = 'DEL001') =>
    api.get('/api/forecast-compare', { params: { station_id: stationId } }),

  history: (stationId = 'DEL001', days = 30) =>
    api.get('/api/forecast-history', { params: { station_id: stationId, days } }),
}

// ─────────────────────────── HEALTH ───────────────────────────────

export const healthAPI = {
  /** @param {object} input — { pm25, pm10, temperature, age, has_asthma, ... } */
  riskAssessment: (input) => api.post('/api/health-risk', input),

  diseaseProbability: (city = 'Delhi') =>
    api.get('/api/disease-probability', { params: { city } }),

  shapExplanation: () => api.get('/api/health-shap'),
}

// ─────────────────────────── ALERTS ───────────────────────────────

export const alertsAPI = {
  send: (data) => api.post('/api/send-alert', data),
  criticalZones: () => api.get('/api/critical-zones'),
  history: (days = 7) => api.get('/api/alert-history', { params: { days } }),
}

// ─────────────────────────── ANALYTICS ────────────────────────────

export const analyticsAPI = {
  heatmap: () => api.get('/api/heatmap'),
  clusters: () => api.get('/api/clusters'),
  trends: (stationId, days = 30, pollutant = 'pm25') =>
    api.get('/api/trends', { params: { station_id: stationId, days, pollutant } }),
  correlationMatrix: () => api.get('/api/correlation-matrix'),
  satelliteAnalysis: (lat = 28.61, lng = 77.21) =>
    api.get('/api/satellite-analysis', { params: { lat, lng } }),
  modelStatus: () => api.get('/api/model-status'),
  summaryStats: () => api.get('/api/summary-stats'),
}

// ─────────────────────────── REALTIME ─────────────────────────────

export const realtimeAPI = {
  allStations: () => api.get('/api/realtime'),
  stations: () => api.get('/api/stations'),
}

// ─────────────────────────── CHATBOT ──────────────────────────────

export const chatAPI = {
  send: (message, context = {}) =>
    api.post('/api/chat', { message, ...context }),
  history: () => api.get('/api/chat/history'),
}

// ─────────────────────────── RECOMMENDATIONS ──────────────────────

export const recommendationsAPI = {
  travel: (city, currentAqi) =>
    api.get('/api/recommendations/travel', { params: { city, current_aqi: currentAqi } }),

  outdoor: (currentAqi, temperature = 30, humidity = 60) =>
    api.get('/api/recommendations/outdoor', { params: { current_aqi: currentAqi, temperature, humidity } }),

  masks: (currentAqi, duration = 1, activity = 'moderate') =>
    api.get('/api/recommendations/masks', { params: { current_aqi: currentAqi, duration, activity } }),

  routes: (originLat, originLng, destLat, destLng) =>
    api.get('/api/recommendations/routes', {
      params: { origin_lat: originLat, origin_lng: originLng, dest_lat: destLat, dest_lng: destLng }
    }),
}

// ─────────────────────────── WEBSOCKET ────────────────────────────

const WS_BASE = BASE_URL.replace(/^http/, 'ws')

export const createRealtimeSocket = (onMessage, onError) => {
  const ws = new WebSocket(`${WS_BASE}/ws/realtime`)
  ws.onmessage = (e) => onMessage(JSON.parse(e.data))
  ws.onerror = (e) => onError?.(e)
  ws.onclose = () => console.log('[WS] Realtime connection closed')
  return ws
}

export const createAlertsSocket = (onAlert, onError) => {
  const ws = new WebSocket(`${WS_BASE}/ws/alerts`)
  ws.onmessage = (e) => onAlert(JSON.parse(e.data))
  ws.onerror = (e) => onError?.(e)
  ws.onclose = () => console.log('[WS] Alerts connection closed')
  return ws
}

export default api
