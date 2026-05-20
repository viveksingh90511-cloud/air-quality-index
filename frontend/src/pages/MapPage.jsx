import React, { useState, useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { realtimeAPI } from '../services/api'

// Fix for default Leaflet icons in React
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})
L.Marker.prototype.options.icon = DefaultIcon

// Helper to color markers based on AQI
function getAqiColor(aqi) {
  if (aqi <= 50) return '#00e400'
  if (aqi <= 100) return '#ffff00'
  if (aqi <= 150) return '#ff7e00'
  if (aqi <= 200) return '#ff0000'
  if (aqi <= 300) return '#8f3f97'
  return '#7e0023'
}

// Map Updater Component
function MapUpdater({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, zoom)
  }, [center, zoom, map])
  return null
}

export default function GeospatialMapPage() {
  const [stations, setStations] = useState([])
  const [loading, setLoading] = useState(true)
  const [center, setCenter] = useState([22.5937, 78.9629]) // Center of India
  const [zoom, setZoom] = useState(5)

  useEffect(() => {
    // Fetch live stations or use simulated data
    realtimeAPI.stations()
      .then(res => {
        setStations(res.stations || [])
        setLoading(false)
      })
      .catch(() => {
        // Fallback simulated data across India
        const simulated = [
          { id: 'DEL001', name: 'Delhi', lat: 28.6139, lng: 77.2090, aqi: 245, pm25: 140 },
          { id: 'MUM001', name: 'Mumbai', lat: 19.0760, lng: 72.8777, aqi: 128, pm25: 72 },
          { id: 'BLR001', name: 'Bangalore', lat: 12.9716, lng: 77.5946, aqi: 75, pm25: 42 },
          { id: 'KOL001', name: 'Kolkata', lat: 22.5726, lng: 88.3639, aqi: 185, pm25: 110 },
          { id: 'CHN001', name: 'Chennai', lat: 13.0827, lng: 80.2707, aqi: 82, pm25: 48 },
          { id: 'HYD001', name: 'Hyderabad', lat: 17.3850, lng: 78.4867, aqi: 95, pm25: 55 },
          { id: 'PUN001', name: 'Pune', lat: 18.5204, lng: 73.8567, aqi: 110, pm25: 65 },
          { id: 'LKN001', name: 'Lucknow', lat: 26.8467, lng: 80.9462, aqi: 260, pm25: 155 },
          { id: 'PAT001', name: 'Patna', lat: 25.5941, lng: 85.1376, aqi: 290, pm25: 180 },
          { id: 'AMD001', name: 'Ahmedabad', lat: 23.0225, lng: 72.5714, aqi: 140, pm25: 85 },
        ]
        setStations(simulated)
        setLoading(false)
      })
  }, [])

  return (
    <div className="animate-fadeIn" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 16 }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: 4 }}>
          🌍 Geospatial Intelligence Map
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Interactive national view of live air quality sensors and pollution hotspots
        </p>
      </div>

      <div className="glass-card" style={{ flex: 1, padding: '4px', overflow: 'hidden', position: 'relative' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)' }}>
            Loading map data...
          </div>
        ) : (
          <MapContainer 
            center={center} 
            zoom={zoom} 
            style={{ height: '100%', width: '100%', borderRadius: 'var(--radius-md)' }}
            theme="dark"
          >
            <MapUpdater center={center} zoom={zoom} />
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />
            {stations.map(station => (
              <CircleMarker
                key={station.id}
                center={[station.lat, station.lng]}
                radius={Math.max(8, station.aqi / 15)}
                pathOptions={{
                  color: getAqiColor(station.aqi),
                  fillColor: getAqiColor(station.aqi),
                  fillOpacity: 0.6,
                  weight: 2
                }}
              >
                <Popup>
                  <div style={{ color: '#000', padding: '4px' }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '4px' }}>
                      {station.name}
                    </h3>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <strong>AQI:</strong> 
                      <span style={{ 
                        color: getAqiColor(station.aqi), 
                        fontWeight: 'bold',
                        backgroundColor: '#fff',
                        padding: '2px 6px',
                        borderRadius: '4px'
                      }}>
                        {station.aqi}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>PM2.5:</strong> <span>{station.pm25} µg/m³</span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  )
}
