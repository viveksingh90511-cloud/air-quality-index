import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ForecastPage from './pages/ForecastPage'
import HealthPage from './pages/HealthPage'
import AlertsPage from './pages/AlertsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import MapPage from './pages/MapPage'
import ChatWidget from './components/ChatWidget'

const NAV_ITEMS = [
  { label: 'MONITORING', items: [
    { path: '/', icon: '📊', label: 'Dashboard', badge: null },
    { path: '/forecast', icon: '📈', label: 'Forecasting', badge: null },
    { path: '/health', icon: '🏥', label: 'Health Risk', badge: null },
  ]},
  { label: 'INTELLIGENCE', items: [
    { path: '/map', icon: '🌍', label: 'Geospatial Map', badge: null },
    { path: '/alerts', icon: '🚨', label: 'Alerts', badge: 3 },
    { path: '/analytics', icon: '📉', label: 'Analytics', badge: null },
  ]},
]

function Sidebar() {
  const location = useLocation()
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🌍</div>
        <span className="sidebar-logo-text">AirQuality AI</span>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(section => (
          <div key={section.label}>
            <div className="nav-section-label">{section.label}</div>
            {section.items.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `nav-item ${isActive || (item.path === '/' && location.pathname === '/') ? 'active' : ''}`
                }
                end={item.path === '/'}
              >
                <span className="nav-item-icon">{item.icon}</span>
                <span>{item.label}</span>
                {item.badge && <span className="nav-item-badge">{item.badge}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
      <div style={{ padding: '16px', borderTop: '1px solid var(--border-glass)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--aqi-good)' }}></span>
          System Operational
        </div>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>v1.0.0 | {new Date().toLocaleDateString()}</div>
      </div>
    </aside>
  )
}

function Header() {
  const [aqi] = useState(127)
  const aqiColor = aqi < 50 ? 'var(--aqi-good)' : aqi < 100 ? 'var(--aqi-moderate)' : aqi < 150 ? 'var(--aqi-unhealthy-sensitive)' : aqi < 200 ? 'var(--aqi-unhealthy)' : 'var(--aqi-very-unhealthy)'

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">Environmental Intelligence Platform</h1>
      </div>
      <div className="header-right">
        <div className="header-aqi-ticker" style={{ borderColor: aqiColor + '40', background: aqiColor + '15' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: aqiColor, boxShadow: `0 0 8px ${aqiColor}` }}></span>
          <span style={{ color: aqiColor }}>AQI {aqi}</span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>Delhi</span>
        </div>
        <button className="notification-btn" id="notifications-btn" aria-label="Notifications">
          🔔
          <span className="notification-badge">3</span>
        </button>
        <div className="user-avatar" id="user-avatar">DU</div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <Header />
        <main className="main-content">
          <div className="page-content">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/health" element={<HealthPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
            </Routes>
          </div>
        </main>
        <ChatWidget />
      </div>
    </Router>
  )
}
