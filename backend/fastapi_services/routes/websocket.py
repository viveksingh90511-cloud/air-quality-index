"""
Air Quality Platform - WebSocket Real-Time Endpoint
FastAPI WebSocket for live AQI streaming to the dashboard.
"""

import asyncio
import json
import random
from datetime import datetime
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info(f"WS connected. Total: {len(self.active)}")

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info(f"WS disconnected. Total: {len(self.active)}")

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()

# Simulated live AQI state
_aqi_state = {
    "DEL001": 245.0, "DEL002": 230.0, "MUM001": 128.0, "MUM002": 115.0,
    "BLR001": 72.0,  "KOL001": 175.0, "CHN001": 82.0,  "HYD001": 90.0,
    "PUN001": 88.0,  "LKN001": 215.0,
}


def _next_aqi(current: float) -> float:
    """Simulate next AQI reading with realistic drift."""
    hour = datetime.now().hour
    diurnal = 12 * (1 if 7 <= hour <= 9 or 17 <= hour <= 20 else -0.3)
    noise = random.gauss(0, 4)
    return max(10.0, min(500.0, current + diurnal + noise))


@router.websocket("/ws/realtime")
async def websocket_realtime(ws: WebSocket):
    """
    WebSocket endpoint streaming live AQI data every 5 seconds.
    Client receives: { type, stations, timestamp }
    Client can send: { "action": "subscribe", "stations": [...] }
    """
    await manager.connect(ws)
    try:
        while True:
            # Update simulated AQI for all stations
            for sid in _aqi_state:
                _aqi_state[sid] = _next_aqi(_aqi_state[sid])

            payload = {
                "type": "aqi_update",
                "timestamp": datetime.now().isoformat(),
                "stations": [
                    {
                        "id": sid,
                        "aqi": round(_aqi_state[sid], 1),
                        "pm25": round(_aqi_state[sid] * 0.55 + random.gauss(0, 3), 1),
                        "pm10": round(_aqi_state[sid] * 1.05 + random.gauss(0, 5), 1),
                        "temperature": round(28 + random.gauss(0, 2), 1),
                        "humidity": round(60 + random.gauss(0, 5), 1),
                    }
                    for sid in _aqi_state
                ],
                "active_alerts": sum(1 for aqi in _aqi_state.values() if aqi > 200),
            }

            await ws.send_json(payload)
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(ws)


@router.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    """
    WebSocket endpoint streaming emergency alerts in real-time.
    Sends alert events only when a critical threshold is crossed.
    """
    await manager.connect(ws)
    last_aqi = dict(_aqi_state)

    try:
        while True:
            alerts = []
            for sid in _aqi_state:
                _aqi_state[sid] = _next_aqi(_aqi_state[sid])
                current = _aqi_state[sid]
                prev = last_aqi.get(sid, current)

                # Alert if crossed threshold
                if current > 300 and prev <= 300:
                    alerts.append({"station_id": sid, "severity": "emergency", "aqi": round(current, 1)})
                elif current > 200 and prev <= 200:
                    alerts.append({"station_id": sid, "severity": "critical", "aqi": round(current, 1)})
                elif current > 150 and prev <= 150:
                    alerts.append({"station_id": sid, "severity": "warning", "aqi": round(current, 1)})

                last_aqi[sid] = current

            if alerts:
                await ws.send_json({
                    "type": "alert_event",
                    "alerts": alerts,
                    "timestamp": datetime.now().isoformat(),
                })

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"Alert WS error: {e}")
        manager.disconnect(ws)
