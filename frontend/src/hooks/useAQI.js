/**
 * Custom React hooks for live AQI data and API calls.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { realtimeAPI, forecastAPI, analyticsAPI, alertsAPI } from '../services/api'
import { createRealtimeSocket } from '../services/api'

// ─── Simulated live data fallback ───────────────────────────

function simulateLiveReading(prev = 100) {
  const hour = new Date().getHours()
  const diurnal = 15 * Math.sin((2 * Math.PI * (hour - 8)) / 24)
  const noise = (Math.random() - 0.5) * 8
  return Math.max(10, Math.min(500, prev + diurnal * 0.05 + noise))
}

// ─────────────────────────────────────────────────────────────
// useAQI — polls live AQI every N seconds
// ─────────────────────────────────────────────────────────────
export function useAQI(intervalMs = 10000) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const aqiRef = useRef(120)

  const fetchData = useCallback(async () => {
    try {
      const result = await realtimeAPI.allStations()
      setData(result)
      setError(null)
    } catch {
      // Fallback to simulated data when API unavailable
      aqiRef.current = simulateLiveReading(aqiRef.current)
      setData({
        data: [
          { station_id: 'DEL001', station_name: 'Anand Vihar', city: 'Delhi', aqi: Math.round(aqiRef.current), pm25: Math.round(aqiRef.current * 0.55) },
          { station_id: 'MUM001', station_name: 'Bandra', city: 'Mumbai', aqi: 128, pm25: 72 },
          { station_id: 'BLR001', station_name: 'Koramangala', city: 'Bangalore', aqi: 75, pm25: 42 },
        ],
        total: 3,
      })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const timer = setInterval(fetchData, intervalMs)
    return () => clearInterval(timer)
  }, [fetchData, intervalMs])

  return { data, loading, error, refetch: fetchData }
}

// ─────────────────────────────────────────────────────────────
// useWebSocket — connects to real-time WS stream
// ─────────────────────────────────────────────────────────────
export function useWebSocket() {
  const [readings, setReadings] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    try {
      wsRef.current = createRealtimeSocket(
        (msg) => {
          if (msg.type === 'aqi_update') {
            setReadings(msg.stations)
            setConnected(true)
          }
        },
        () => setConnected(false)
      )
      wsRef.current.onopen = () => setConnected(true)
      wsRef.current.onclose = () => setConnected(false)
    } catch {
      setConnected(false)
    }

    return () => wsRef.current?.close()
  }, [])

  return { readings, connected }
}

// ─────────────────────────────────────────────────────────────
// useForecast
// ─────────────────────────────────────────────────────────────
export function useForecast(stationId = 'DEL001', horizon = '7d') {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await forecastAPI.predict(stationId, horizon)
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
      // Simulated fallback
      const now = new Date()
      const hoursMap = { '24h': 24, '3d': 72, '7d': 168, '30d': 720 }
      const hours = hoursMap[horizon] || 168
      const preds = Array.from({ length: hours }, (_, h) => {
        const hour = (now.getHours() + h) % 24
        return Math.round(100 + 25 * Math.sin((2 * Math.PI * (hour - 8)) / 24) + (Math.random() - 0.5) * 15)
      })
      setData({ primary: { predictions: preds, model: 'simulated' }, models_used: ['simulated'] })
    } finally {
      setLoading(false)
    }
  }, [stationId, horizon])

  useEffect(() => { fetch() }, [fetch])
  return { data, loading, error, refetch: fetch }
}

// ─────────────────────────────────────────────────────────────
// useAlerts
// ─────────────────────────────────────────────────────────────
export function useAlerts(days = 7) {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    alertsAPI.history(days)
      .then(r => setAlerts(r.alerts || []))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false))
  }, [days])

  return { alerts, loading }
}

// ─────────────────────────────────────────────────────────────
// useSummaryStats
// ─────────────────────────────────────────────────────────────
export function useSummaryStats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsAPI.summaryStats()
      .then(setStats)
      .catch(() => setStats({
        total_stations: 10, active_sensors: 18, alerts_today: 5,
        avg_aqi_national: 142.3, cities_monitored: 8, models_active: 7, uptime_pct: 99.7,
      }))
      .finally(() => setLoading(false))
  }, [])

  return { stats, loading }
}

// ─────────────────────────────────────────────────────────────
// useAQIColor — returns color for a given AQI value
// ─────────────────────────────────────────────────────────────
export function useAQIColor(aqi) {
  if (aqi <= 50)  return '#00e400'
  if (aqi <= 100) return '#ffff00'
  if (aqi <= 150) return '#ff7e00'
  if (aqi <= 200) return '#ff0000'
  if (aqi <= 300) return '#8f3f97'
  return '#7e0023'
}
