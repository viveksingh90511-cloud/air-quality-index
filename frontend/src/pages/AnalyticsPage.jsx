import React, { useMemo } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function AnalyticsPage() {
  const features = ['PM2.5', 'PM10', 'CO', 'SO₂', 'NO₂', 'O₃', 'Temp', 'Humidity', 'Wind']
  const matrix = [
    [1.00, 0.85, 0.62, 0.45, 0.58, -0.22, 0.15, -0.35, -0.42],
    [0.85, 1.00, 0.55, 0.50, 0.52, -0.18, 0.18, -0.30, -0.38],
    [0.62, 0.55, 1.00, 0.35, 0.68, -0.15, 0.10, -0.25, -0.30],
    [0.45, 0.50, 0.35, 1.00, 0.42, -0.10, 0.08, -0.20, -0.25],
    [0.58, 0.52, 0.68, 0.42, 1.00, 0.25, 0.22, -0.28, -0.35],
    [-0.22, -0.18, -0.15, -0.10, 0.25, 1.00, 0.55, -0.15, 0.10],
    [0.15, 0.18, 0.10, 0.08, 0.22, 0.55, 1.00, -0.45, 0.05],
    [-0.35, -0.30, -0.25, -0.20, -0.28, -0.15, -0.45, 1.00, 0.15],
    [-0.42, -0.38, -0.30, -0.25, -0.35, 0.10, 0.05, 0.15, 1.00],
  ]

  const getCorrelationColor = (val) => {
    if (val >= 0.6) return '#00e400'
    if (val >= 0.3) return '#10b981'
    if (val >= 0) return '#2d3748'
    if (val >= -0.3) return '#f59e0b'
    return '#ef4444'
  }

  const trendData = useMemo(() => {
    const data = []
    for (let d = 30; d >= 0; d--) {
      const date = new Date(Date.now() - d * 86400000)
      data.push({
        date: date.toLocaleDateString([], { month: 'short', day: 'numeric' }),
        pm25: Math.round(80 + 30 * Math.sin((2 * Math.PI * d) / 30) + (Math.random() - 0.5) * 20),
        pm10: Math.round(130 + 40 * Math.sin((2 * Math.PI * d) / 30) + (Math.random() - 0.5) * 30),
        aqi: Math.round(100 + 35 * Math.sin((2 * Math.PI * d) / 30) + (Math.random() - 0.5) * 25),
      })
    }
    return data
  }, [])

  const seasonalData = useMemo(() => ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((m, i) => ({
    month: m,
    aqi: Math.round([180, 160, 130, 100, 90, 60, 45, 50, 70, 120, 200, 220][i] + (Math.random() - 0.5) * 10),
  })), [])

  return (
    <div className="animate-fadeIn">
      <h1 style={{ marginBottom: 4 }}>📉 Advanced Analytics</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 20, fontSize: '0.85rem' }}>
        Deep analytics with correlation matrices, trend analysis, and seasonal decomposition
      </p>

      {/* Correlation Matrix */}
      <div className="glass-card" style={{ marginBottom: 20 }}>
        <div className="card-header"><h3>🔗 Pollutant Correlation Matrix</h3></div>
        <div style={{ padding: 20, overflowX: 'auto' }}>
          <table style={{ borderCollapse: 'collapse', margin: '0 auto' }}>
            <thead>
              <tr>
                <th style={{ padding: 8 }}></th>
                {features.map(f => <th key={f} style={{ padding: '6px 10px', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500, writingMode: 'vertical-lr', transform: 'rotate(180deg)', textAlign: 'center', height: 70 }}>{f}</th>)}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={i}>
                  <td style={{ padding: '6px 12px', fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500, textAlign: 'right' }}>{features[i]}</td>
                  {row.map((val, j) => (
                    <td key={j} style={{
                      padding: 0, width: 44, height: 44, textAlign: 'center',
                      background: i === j ? 'rgba(99,102,241,0.15)' : `${getCorrelationColor(val)}${Math.round(Math.abs(val) * 40).toString(16).padStart(2, '0')}`,
                      fontSize: '0.65rem', fontFamily: 'var(--font-mono)',
                      color: Math.abs(val) > 0.4 ? 'var(--text-primary)' : 'var(--text-muted)',
                      fontWeight: Math.abs(val) > 0.6 ? 700 : 400,
                      borderRadius: 4, cursor: 'default',
                    }} title={`${features[i]} × ${features[j]}: ${val.toFixed(2)}`}>
                      {val.toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid-2">
        {/* 30-Day Trend */}
        <div className="glass-card">
          <div className="card-header"><h3>📈 30-Day Pollution Trend</h3></div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="aqiTrendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" stroke="#4a5568" fontSize={10} />
                <YAxis stroke="#4a5568" fontSize={11} />
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Area type="monotone" dataKey="aqi" stroke="#6366f1" strokeWidth={2} fill="url(#aqiTrendGrad)" name="AQI" />
                <Area type="monotone" dataKey="pm25" stroke="#8b5cf6" strokeWidth={1.5} fill="none" name="PM2.5" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Seasonal Pattern */}
        <div className="glass-card">
          <div className="card-header"><h3>🗓️ Seasonal AQI Pattern</h3></div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={seasonalData}>
                <defs>
                  <linearGradient id="seasonGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" stroke="#4a5568" fontSize={11} />
                <YAxis stroke="#4a5568" fontSize={11} />
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Area type="monotone" dataKey="aqi" stroke="#f59e0b" strokeWidth={2} fill="url(#seasonGrad)" name="Avg AQI" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="glass-card" style={{ marginTop: 20 }}>
        <div className="card-header"><h3>💡 AI-Generated Insights</h3></div>
        <div style={{ padding: 20, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {[
            { icon: '📊', title: 'Strong PM Correlation', text: 'PM2.5 and PM10 show 0.85 correlation — suggests common vehicular/industrial source.', color: '#6366f1' },
            { icon: '🌡️', title: 'Temperature Inversion', text: 'Winter months (Nov-Feb) show 2.5x higher AQI due to temperature inversion trapping pollutants.', color: '#f59e0b' },
            { icon: '🌧️', title: 'Monsoon Cleaning', text: 'Monsoon season (Jun-Sep) reduces AQI by 60-70% through rain washout of particulate matter.', color: '#10b981' },
            { icon: '🌬️', title: 'Wind Negative Correlation', text: 'Wind speed shows -0.42 correlation with PM2.5 — higher winds disperse pollutants effectively.', color: '#06b6d4' },
          ].map((insight, i) => (
            <div key={i} style={{ padding: 16, borderRadius: 'var(--radius-sm)', background: `${insight.color}08`, border: `1px solid ${insight.color}20` }}>
              <div style={{ fontSize: '1.2rem', marginBottom: 8 }}>{insight.icon}</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 4, color: insight.color }}>{insight.title}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{insight.text}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
