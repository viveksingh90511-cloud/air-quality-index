import React, { useState, useEffect, useMemo } from 'react'
import { AreaChart, Area, LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { apiClient, endpoints } from '../api/client'

// ===================== SIMULATED DATA =====================
function generateHourlyData(hours = 72) {
  const data = []
  const now = new Date()
  let base = 80 + Math.random() * 60
  for (let i = hours; i >= 0; i--) {
    const ts = new Date(now - i * 3600000)
    const hour = ts.getHours()
    const diurnal = 25 * Math.sin((2 * Math.PI * (hour - 8)) / 24)
    const noise = (Math.random() - 0.5) * 20
    base += (Math.random() - 0.5) * 3
    const aqi = Math.max(10, Math.min(350, base + diurnal + noise))
    data.push({
      time: ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      date: ts.toLocaleDateString([], { month: 'short', day: 'numeric' }),
      aqi: Math.round(aqi),
      pm25: Math.round(aqi * 0.6 + (Math.random() - 0.5) * 10),
      pm10: Math.round(aqi * 1.1 + (Math.random() - 0.5) * 20),
      co: +(aqi * 0.015 + Math.random() * 0.5).toFixed(2),
      no2: Math.round(aqi * 0.3 + (Math.random() - 0.5) * 8),
      o3: Math.round(40 - aqi * 0.05 + Math.random() * 10),
      temperature: +(28 + 5 * Math.sin((2 * Math.PI * (hour - 6)) / 24) + Math.random() * 2).toFixed(1),
      humidity: Math.round(60 + Math.random() * 20 - 10),
    })
  }
  return data
}

function getAqiInfo(aqi) {
  if (aqi <= 50) return { label: 'Good', color: '#00e400', emoji: '😊' }
  if (aqi <= 100) return { label: 'Moderate', color: '#ffff00', emoji: '😐' }
  if (aqi <= 150) return { label: 'Unhealthy (Sensitive)', color: '#ff7e00', emoji: '😷' }
  if (aqi <= 200) return { label: 'Unhealthy', color: '#ff0000', emoji: '🤢' }
  if (aqi <= 300) return { label: 'Very Unhealthy', color: '#8f3f97', emoji: '🤮' }
  return { label: 'Hazardous', color: '#7e0023', emoji: '☠️' }
}

// ===================== AQI GAUGE COMPONENT =====================
function AQIGauge({ value = 127, size = 200 }) {
  const info = getAqiInfo(value)
  const radius = (size - 24) / 2
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(value / 500, 1)
  const dashOffset = circumference * (1 - progress)

  return (
    <div className="aqi-gauge-container">
      <div className="aqi-gauge" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle className="aqi-gauge-bg" cx={size/2} cy={size/2} r={radius} />
          <circle
            className="aqi-gauge-fill"
            cx={size/2} cy={size/2} r={radius}
            stroke={info.color}
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ filter: `drop-shadow(0 0 10px ${info.color})` }}
          />
        </svg>
        <div className="aqi-gauge-value">
          <div className="aqi-gauge-number" style={{ color: info.color }}>{value}</div>
          <div className="aqi-gauge-label">{info.emoji} {info.label}</div>
        </div>
      </div>
    </div>
  )
}

// ===================== ALERT FEED COMPONENT =====================
function AlertFeed() {
  const alerts = [
    { id: 1, severity: 'emergency', city: 'Delhi', aqi: 310, msg: 'Hazardous AQI levels in Anand Vihar', time: '2 min ago' },
    { id: 2, severity: 'critical', city: 'Lucknow', aqi: 245, msg: 'Critical pollution in Gomti Nagar', time: '15 min ago' },
    { id: 3, severity: 'warning', city: 'Kolkata', aqi: 180, msg: 'Elevated PM2.5 in Jadavpur area', time: '1 hr ago' },
    { id: 4, severity: 'warning', city: 'Mumbai', aqi: 135, msg: 'Moderate pollution in Bandra West', time: '2 hrs ago' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: 16 }}>
      {alerts.map(alert => (
        <div key={alert.id} className="animate-fadeInUp" style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-sm)',
          background: alert.severity === 'emergency' ? 'rgba(126,0,35,0.15)' : alert.severity === 'critical' ? 'rgba(255,0,0,0.08)' : 'rgba(255,255,0,0.05)',
          border: `1px solid ${alert.severity === 'emergency' ? 'rgba(126,0,35,0.3)' : alert.severity === 'critical' ? 'rgba(255,0,0,0.15)' : 'rgba(255,255,0,0.1)'}`,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <span className={`alert-badge alert-${alert.severity}`} style={{ marginRight: 8 }}>{alert.severity}</span>
            <span style={{ fontSize: '0.85rem' }}>{alert.msg}</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{alert.time}</span>
        </div>
      ))}
    </div>
  )
}

// ===================== CITY AQI COMPARISON =====================
function CityComparison() {
  const cities = [
    { name: 'Delhi', aqi: 258 }, { name: 'Lucknow', aqi: 210 },
    { name: 'Kolkata', aqi: 165 }, { name: 'Mumbai', aqi: 128 },
    { name: 'Pune', aqi: 88 }, { name: 'Hyderabad', aqi: 92 },
    { name: 'Chennai', aqi: 72 }, { name: 'Bangalore', aqi: 65 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={cities} layout="vertical" margin={{ left: 10, right: 20 }}>
        <XAxis type="number" stroke="#4a5568" fontSize={11} />
        <YAxis type="category" dataKey="name" stroke="#94a3b8" fontSize={12} width={80} />
        <Tooltip
          contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 13 }}
        />
        <Bar dataKey="aqi" radius={[0, 6, 6, 0]} fill="#6366f1">
          {cities.map((entry, i) => {
            const info = getAqiInfo(entry.aqi)
            return <rect key={i} fill={info.color + 'cc'} />
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// ===================== DASHBOARD PAGE =====================
export default function DashboardPage() {
  const [data, setData] = useState(generateHourlyData(72))
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function loadRealtime() {
      try {
        setLoading(true)
        const res = await apiClient.get(endpoints.realtime)
        if (res && res.data && res.data.length > 0) {
          // Find Delhi data (or first station)
          const stationData = res.data.find(s => s.city === 'Delhi') || res.data[0]
          
          setData(prev => {
            const newData = [...prev]
            // Overwrite the most recent data point with real data
            newData[newData.length - 1] = {
              ...newData[newData.length - 1],
              aqi: stationData.aqi || newData[newData.length - 1].aqi,
              pm25: stationData.pm25 || newData[newData.length - 1].pm25,
              pm10: stationData.pm10 || newData[newData.length - 1].pm10,
              temperature: stationData.temperature || newData[newData.length - 1].temperature,
              humidity: stationData.humidity || newData[newData.length - 1].humidity,
            }
            return newData
          })
        }
      } catch (err) {
        console.error("Failed to fetch realtime data:", err)
      } finally {
        setLoading(false)
      }
    }
    loadRealtime()
  }, [])

  const current = data[data.length - 1]
  const prev = data[data.length - 2]

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}>Loading live data...</div>

  const metrics = [
    { label: '🌫️ AQI', value: current.aqi, prev: prev.aqi, unit: '', color: getAqiInfo(current.aqi).color },
    { label: '💨 PM2.5', value: current.pm25, prev: prev.pm25, unit: 'µg/m³', color: '#6366f1' },
    { label: '🌪️ PM10', value: current.pm10, prev: prev.pm10, unit: 'µg/m³', color: '#8b5cf6' },
    { label: '🔥 CO', value: current.co, prev: prev.co, unit: 'mg/m³', color: '#f59e0b' },
    { label: '🧪 NO₂', value: current.no2, prev: prev.no2, unit: 'µg/m³', color: '#ef4444' },
    { label: '🌡️ Temp', value: current.temperature, prev: prev.temperature, unit: '°C', color: '#06b6d4' },
  ]

  const radarData = [
    { name: 'PM2.5', value: Math.min(current.pm25 / 2.5, 100), fullMark: 100 },
    { name: 'PM10', value: Math.min(current.pm10 / 4.3, 100), fullMark: 100 },
    { name: 'CO', value: Math.min(current.co * 20, 100), fullMark: 100 },
    { name: 'NO₂', value: Math.min(current.no2 / 1.8, 100), fullMark: 100 },
    { name: 'O₃', value: Math.min(current.o3 / 1.6, 100), fullMark: 100 },
    { name: 'SO₂', value: Math.min(30 / 0.8, 100), fullMark: 100 },
  ]

  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: 4 }}>
          Real-Time Air Quality Dashboard
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Monitoring 10 stations across 8 Indian cities • Updated {new Date().toLocaleTimeString()}
        </p>
      </div>

      {/* Metric Cards */}
      <div className="metric-grid stagger-children">
        {metrics.map((m, i) => {
          const change = +(m.value - m.prev).toFixed(1)
          return (
            <div key={i} className="metric-card">
              <div className="metric-label">{m.label}</div>
              <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{m.unit}</div>
              <div className={`metric-change ${change > 0 ? 'negative' : 'positive'}`}>
                {change > 0 ? '↑' : '↓'} {Math.abs(change)}
              </div>
            </div>
          )
        })}
      </div>

      {/* Main Charts Row */}
      <div className="grid-dashboard" style={{ marginBottom: 20 }}>
        {/* AQI Trend Chart */}
        <div className="glass-card">
          <div className="card-header">
            <h3>📈 AQI Trend (72 Hours)</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>All Stations Average</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.filter((_, i) => i % 3 === 0)}>
                <defs>
                  <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="time" stroke="#4a5568" fontSize={10} interval={3} />
                <YAxis stroke="#4a5568" fontSize={11} />
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 13 }} />
                <Area type="monotone" dataKey="aqi" stroke="#6366f1" strokeWidth={2} fill="url(#aqiGradient)" />
                {/* Threshold lines */}
                <Line type="monotone" dataKey={() => 100} stroke="#ffff00" strokeDasharray="5 5" strokeWidth={1} dot={false} name="Moderate" />
                <Line type="monotone" dataKey={() => 200} stroke="#ff0000" strokeDasharray="5 5" strokeWidth={1} dot={false} name="Unhealthy" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AQI Gauge + Radar */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-header">
            <h3>🎯 Current AQI</h3>
          </div>
          <AQIGauge value={current.aqi} size={180} />
          <div style={{ flex: 1, padding: '0 16px 16px' }}>
            <ResponsiveContainer width="100%" height={160}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
                <PolarRadiusAxis stroke="rgba(255,255,255,0.05)" fontSize={9} />
                <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.25} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid-dashboard">
        {/* City Comparison */}
        <div className="glass-card">
          <div className="card-header">
            <h3>🏙️ City AQI Comparison</h3>
          </div>
          <div className="chart-container">
            <CityComparison />
          </div>
        </div>

        {/* Live Alerts */}
        <div className="glass-card">
          <div className="card-header">
            <h3>🚨 Live Alerts</h3>
            <span className="alert-badge alert-emergency">3 Active</span>
          </div>
          <AlertFeed />
        </div>
      </div>

      {/* Multi-pollutant mini charts */}
      <div className="grid-3" style={{ marginTop: 20 }}>
        {[
          { key: 'pm25', label: 'PM2.5 Trend', color: '#6366f1' },
          { key: 'temperature', label: 'Temperature', color: '#06b6d4' },
          { key: 'humidity', label: 'Humidity (%)', color: '#10b981' },
        ].map(chart => (
          <div key={chart.key} className="glass-card">
            <div className="card-header"><h3>{chart.label}</h3></div>
            <div style={{ padding: 16 }}>
              <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={data.filter((_, i) => i % 4 === 0)}>
                  <defs>
                    <linearGradient id={`grad-${chart.key}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chart.color} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={chart.color} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area type="monotone" dataKey={chart.key} stroke={chart.color} strokeWidth={2} fill={`url(#grad-${chart.key})`} />
                  <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
