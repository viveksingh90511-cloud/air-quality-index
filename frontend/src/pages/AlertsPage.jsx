import React from 'react'

const ALERTS = [
  { id: 1, severity: 'emergency', city: 'Delhi', zone: 'Anand Vihar', aqi: 310, msg: 'Hazardous AQI: Immediate indoor shelter advised for all residents', status: 'active', time: '2 min ago', actions: { sms: true, email: true, hospital: true, govt: true } },
  { id: 2, severity: 'critical', city: 'Lucknow', zone: 'Gomti Nagar', aqi: 245, msg: 'Critical PM2.5 spike detected — respiratory advisory issued', status: 'active', time: '15 min ago', actions: { sms: true, email: true, hospital: true, govt: true } },
  { id: 3, severity: 'warning', city: 'Kolkata', zone: 'Jadavpur', aqi: 180, msg: 'Elevated pollution — sensitive groups should stay indoors', status: 'acknowledged', time: '1 hr ago', actions: { sms: false, email: true, hospital: false, govt: false } },
  { id: 4, severity: 'warning', city: 'Mumbai', zone: 'Bandra', aqi: 135, msg: 'Moderate air quality decline near Western Express Highway', status: 'resolved', time: '3 hrs ago', actions: { sms: false, email: true, hospital: false, govt: false } },
  { id: 5, severity: 'critical', city: 'Delhi', zone: 'ITO', aqi: 265, msg: 'Very unhealthy conditions — school closure recommended', status: 'active', time: '30 min ago', actions: { sms: true, email: true, hospital: false, govt: true } },
]

const SEV_STYLE = {
  emergency: { bg: 'rgba(126,0,35,0.15)', border: 'rgba(126,0,35,0.3)', color: '#ff4466', icon: '🚨' },
  critical: { bg: 'rgba(255,68,68,0.08)', border: 'rgba(255,68,68,0.2)', color: '#ff4444', icon: '⚠️' },
  warning: { bg: 'rgba(255,255,0,0.05)', border: 'rgba(255,255,0,0.12)', color: '#ffff00', icon: '⚡' },
}

const STATUS_STYLE = {
  active: { bg: '#ff444420', color: '#ff4444', label: '● Active' },
  acknowledged: { bg: '#f59e0b20', color: '#f59e0b', label: '◉ Acknowledged' },
  resolved: { bg: '#00e40020', color: '#00e400', label: '✓ Resolved' },
}

export default function AlertsPage() {
  const activeCount = ALERTS.filter(a => a.status === 'active').length

  return (
    <div className="animate-fadeIn">
      <h1 style={{ marginBottom: 4 }}>🚨 Alert Management</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 20, fontSize: '0.85rem' }}>
        SVM + Random Forest ensemble classification with automated alert routing
      </p>

      {/* Summary Cards */}
      <div className="metric-grid stagger-children" style={{ marginBottom: 24 }}>
        {[
          { label: '🚨 Active Alerts', value: activeCount, color: '#ff4444' },
          { label: '⚠️ Total Today', value: ALERTS.length, color: '#f59e0b' },
          { label: '✅ Resolved', value: ALERTS.filter(a => a.status === 'resolved').length, color: '#00e400' },
          { label: '🏥 Hospital Routed', value: ALERTS.filter(a => a.actions.hospital).length, color: '#06b6d4' },
          { label: '📱 SMS Sent', value: ALERTS.filter(a => a.actions.sms).length, color: '#8b5cf6' },
          { label: '🏛️ Govt Notified', value: ALERTS.filter(a => a.actions.govt).length, color: '#ec4899' },
        ].map((m, i) => (
          <div key={i} className="metric-card">
            <div className="metric-label">{m.label}</div>
            <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* Alert List */}
      <div className="glass-card">
        <div className="card-header">
          <h3>📋 Alert Feed</h3>
          <span className="alert-badge alert-emergency">{activeCount} Active</span>
        </div>
        <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {ALERTS.map(alert => {
            const sev = SEV_STYLE[alert.severity]
            const stat = STATUS_STYLE[alert.status]
            return (
              <div key={alert.id} className="animate-fadeInUp" style={{
                padding: '16px 20px', borderRadius: 'var(--radius-md)',
                background: sev.bg, border: `1px solid ${sev.border}`,
                display: 'flex', flexDirection: 'column', gap: 10,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: '1.2rem' }}>{sev.icon}</span>
                    <span className={`alert-badge alert-${alert.severity}`}>{alert.severity}</span>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{alert.city} — {alert.zone}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: sev.color, fontWeight: 700 }}>AQI {alert.aqi}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ padding: '3px 10px', borderRadius: 'var(--radius-full)', background: stat.bg, color: stat.color, fontSize: '0.7rem', fontWeight: 600 }}>{stat.label}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{alert.time}</span>
                  </div>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>{alert.msg}</p>
                <div style={{ display: 'flex', gap: 8 }}>
                  {alert.actions.sms && <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 'var(--radius-full)', background: 'rgba(99,102,241,0.1)', color: 'var(--primary-300)', border: '1px solid rgba(99,102,241,0.2)' }}>📱 SMS</span>}
                  {alert.actions.email && <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 'var(--radius-full)', background: 'rgba(6,182,212,0.1)', color: 'var(--accent-cyan)', border: '1px solid rgba(6,182,212,0.2)' }}>📧 Email</span>}
                  {alert.actions.hospital && <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 'var(--radius-full)', background: 'rgba(239,68,68,0.1)', color: 'var(--accent-red)', border: '1px solid rgba(239,68,68,0.2)' }}>🏥 Hospital</span>}
                  {alert.actions.govt && <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 'var(--radius-full)', background: 'rgba(236,72,153,0.1)', color: 'var(--accent-pink)', border: '1px solid rgba(236,72,153,0.2)' }}>🏛️ Govt</span>}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
