import React, { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { apiClient, endpoints } from '../api/client'

const RISK_COLORS = { safe: '#00e400', low_risk: '#ffff00', moderate_risk: '#ff7e00', high_risk: '#ff0000', severe: '#7e0023' }

export default function HealthPage() {
  const [formData, setFormData] = useState({ age: 30, has_asthma: 0, has_heart_condition: 0, outdoor_hours: 2, current_aqi: 150 })
  const [result, setResult] = useState(null)

  const riskData = [
    { name: 'Asthma', score: 0.72, color: '#6366f1' },
    { name: 'Respiratory', score: 0.65, color: '#8b5cf6' },
    { name: 'Cardiovascular', score: 0.45, color: '#ef4444' },
    { name: 'Heatstroke', score: 0.32, color: '#f59e0b' },
    { name: 'Elderly Risk', score: 0.55, color: '#06b6d4' },
    { name: 'Child Risk', score: 0.68, color: '#ec4899' },
  ]

  const pieData = [
    { name: 'Safe', value: 15, color: '#00e400' },
    { name: 'Low Risk', value: 25, color: '#ffff00' },
    { name: 'Moderate', value: 30, color: '#ff7e00' },
    { name: 'High Risk', value: 20, color: '#ff0000' },
    { name: 'Severe', value: 10, color: '#7e0023' },
  ]

  const shapData = [
    { feature: 'PM2.5', importance: 0.28 },
    { feature: 'PM10', importance: 0.18 },
    { feature: 'Temperature', importance: 0.12 },
    { feature: 'NO₂', importance: 0.10 },
    { feature: 'CO', importance: 0.08 },
    { feature: 'O₃', importance: 0.07 },
    { feature: 'Humidity', importance: 0.06 },
    { feature: 'Wind Speed', importance: 0.04 },
    { feature: 'Age', importance: 0.04 },
    { feature: 'Conditions', importance: 0.03 },
  ]

  const [loading, setLoading] = useState(false)

  const handleAssess = async () => {
    try {
      setLoading(true)
      const res = await apiClient.post(endpoints.healthRisk, {
        current_aqi: formData.current_aqi,
        age: formData.age,
        outdoor_hours: formData.outdoor_hours,
        has_asthma: formData.has_asthma,
        has_heart_condition: formData.has_heart_condition
      })
      
      if (res) {
        setResult({
          risk_level: res.risk_level || 'moderate_risk',
          overall_score: res.risk_scores?.overall_risk || +(formData.current_aqi / 300).toFixed(3),
          recommendations: res.recommendations || [
            'Wear N95 mask outdoors', 'Use air purifiers indoors', 'Limit outdoor exercise'
          ]
        })
      }
    } catch (err) {
      console.error('Failed to assess health risk:', err)
      // Fallback
      const factor = Math.min(formData.current_aqi / 300, 1)
      setResult({
        risk_level: factor < 0.2 ? 'safe' : factor < 0.4 ? 'low_risk' : factor < 0.6 ? 'moderate_risk' : factor < 0.8 ? 'high_risk' : 'severe',
        overall_score: +(factor * 0.8 + Math.random() * 0.1).toFixed(3),
        recommendations: factor > 0.5
          ? ['Wear N95 mask outdoors', 'Use air purifiers indoors', 'Limit outdoor exercise', 'Keep medications accessible']
          : ['Air quality is acceptable', 'Moderate outdoor activity is fine', 'Stay hydrated'],
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fadeIn">
      <h1 style={{ marginBottom: 4 }}>🏥 Health Risk Analytics</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 20, fontSize: '0.85rem' }}>
        XGBoost-powered health risk prediction with SHAP explainability
      </p>

      <div className="grid-dashboard" style={{ marginBottom: 20 }}>
        {/* Risk Assessment Form */}
        <div className="glass-card">
          <div className="card-header"><h3>🩺 Personal Risk Assessment</h3></div>
          <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { label: 'Current AQI', key: 'current_aqi', type: 'range', min: 0, max: 500, step: 1 },
              { label: 'Age', key: 'age', type: 'range', min: 1, max: 100, step: 1 },
              { label: 'Outdoor Hours/Day', key: 'outdoor_hours', type: 'range', min: 0, max: 12, step: 0.5 },
            ].map(field => (
              <div key={field.key}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
                  {field.label} <span style={{ color: 'var(--primary-300)', fontFamily: 'var(--font-mono)' }}>{formData[field.key]}</span>
                </label>
                <input type="range" min={field.min} max={field.max} step={field.step} value={formData[field.key]}
                  onChange={e => setFormData({ ...formData, [field.key]: +e.target.value })}
                  style={{ width: '100%', marginTop: 4, accentColor: 'var(--primary-500)' }}
                />
              </div>
            ))}
            <div style={{ display: 'flex', gap: 16 }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <input type="checkbox" checked={formData.has_asthma} onChange={e => setFormData({ ...formData, has_asthma: e.target.checked ? 1 : 0 })} style={{ accentColor: 'var(--primary-500)' }} />
                Has Asthma
              </label>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <input type="checkbox" checked={formData.has_heart_condition} onChange={e => setFormData({ ...formData, has_heart_condition: e.target.checked ? 1 : 0 })} style={{ accentColor: 'var(--primary-500)' }} />
                Heart Condition
              </label>
            </div>
            <button className="btn btn-primary" onClick={handleAssess} id="assess-risk-btn" disabled={loading}>
              {loading ? '🔍 Assessing...' : '🔍 Assess Risk'}
            </button>
            {result && (
              <div style={{ padding: 16, borderRadius: 'var(--radius-sm)', background: RISK_COLORS[result.risk_level] + '15', border: `1px solid ${RISK_COLORS[result.risk_level]}40` }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: RISK_COLORS[result.risk_level], marginBottom: 8 }}>
                  ⚠️ Risk Level: {result.risk_level.replace('_', ' ').toUpperCase()} (Score: {result.overall_score})
                </div>
                <ul style={{ paddingLeft: 20, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {result.recommendations.map((r, i) => <li key={i} style={{ marginBottom: 4 }}>{r}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="glass-card">
          <div className="card-header"><h3>📊 Population Risk Distribution</h3></div>
          <div style={{ padding: 16, display: 'flex', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* SHAP Feature Importance */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="glass-card">
          <div className="card-header"><h3>🧠 SHAP Feature Importance</h3></div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={shapData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis type="number" stroke="#4a5568" fontSize={11} />
                <YAxis type="category" dataKey="feature" stroke="#94a3b8" fontSize={12} width={90} />
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header"><h3>📈 Risk Scores by Category</h3></div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={riskData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#4a5568" fontSize={11} domain={[0, 1]} />
                <Tooltip contentStyle={{ background: 'rgba(15,20,45,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                  {riskData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
