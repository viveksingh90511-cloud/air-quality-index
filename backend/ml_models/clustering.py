"""
Air Quality Platform - K-Means + DBSCAN Hotspot Detection Module
Spatial clustering for pollution hotspot identification.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)


class HotspotDetector:
    """
    Spatial clustering using K-Means and DBSCAN for:
    - Pollution hotspots
    - Industrial contamination zones
    - High-risk urban regions
    - Traffic pollution corridors
    """

    def __init__(self):
        self.kmeans_model = None
        self.dbscan_model = None
        self.clusters = []
        self.is_fitted = False

    def fit_kmeans(self, data: pd.DataFrame, n_clusters: int = 5) -> dict:
        """Perform K-Means clustering on pollution data."""
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score

            features = ["latitude", "longitude", "pm25", "pm10", "aqi"]
            available = [f for f in features if f in data.columns]
            X = data[available].dropna().values

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = self.kmeans_model.fit_predict(X_scaled)

            sil_score = silhouette_score(X_scaled, labels) if len(set(labels)) > 1 else 0

            clusters = self._extract_clusters(data, labels, "kmeans")
            self.clusters = clusters
            self.is_fitted = True

            return {
                "algorithm": "kmeans",
                "n_clusters": n_clusters,
                "silhouette_score": round(sil_score, 4),
                "clusters": clusters,
                "generated_at": datetime.now().isoformat(),
            }
        except ImportError:
            return self._simulated_clusters(n_clusters)

    def fit_dbscan(self, data: pd.DataFrame, eps: float = 0.3, min_samples: int = 5) -> dict:
        """Perform DBSCAN clustering for density-based hotspot detection."""
        try:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler

            features = ["latitude", "longitude", "pm25", "pm10"]
            available = [f for f in features if f in data.columns]
            X = data[available].dropna().values

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            self.dbscan_model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = self.dbscan_model.fit_predict(X_scaled)

            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = list(labels).count(-1)

            clusters = self._extract_clusters(data, labels, "dbscan")

            return {
                "algorithm": "dbscan",
                "n_clusters": n_clusters,
                "n_noise_points": n_noise,
                "eps": eps,
                "min_samples": min_samples,
                "clusters": clusters,
                "generated_at": datetime.now().isoformat(),
            }
        except ImportError:
            return self._simulated_clusters(5)

    def detect_hotspots(self, data: pd.DataFrame = None) -> dict:
        """Run full hotspot detection pipeline with both algorithms."""
        if data is None or data.empty:
            return self._simulated_clusters(6)

        kmeans_result = self.fit_kmeans(data)
        dbscan_result = self.fit_dbscan(data)

        return {
            "kmeans": kmeans_result,
            "dbscan": dbscan_result,
            "combined_hotspots": self._merge_hotspots(
                kmeans_result.get("clusters", []),
                dbscan_result.get("clusters", [])
            ),
            "generated_at": datetime.now().isoformat(),
        }

    def _extract_clusters(self, data: pd.DataFrame, labels: np.ndarray, algorithm: str) -> list:
        """Extract cluster information from labels."""
        clusters = []
        data_copy = data.copy()
        data_copy["cluster_label"] = labels

        for label in sorted(set(labels)):
            if label == -1:
                continue
            cluster_data = data_copy[data_copy["cluster_label"] == label]

            avg_aqi = cluster_data["aqi"].mean() if "aqi" in cluster_data.columns else random.uniform(50, 200)

            if avg_aqi < 50: risk = "safe"
            elif avg_aqi < 100: risk = "low_risk"
            elif avg_aqi < 200: risk = "moderate_risk"
            elif avg_aqi < 300: risk = "high_risk"
            else: risk = "severe"

            clusters.append({
                "cluster_id": int(label),
                "algorithm": algorithm,
                "centroid_lat": round(float(cluster_data["latitude"].mean()), 6),
                "centroid_lng": round(float(cluster_data["longitude"].mean()), 6),
                "radius_km": round(self._calc_radius(cluster_data), 2),
                "num_points": len(cluster_data),
                "avg_aqi": round(float(avg_aqi), 1),
                "max_aqi": round(float(cluster_data["aqi"].max()), 1) if "aqi" in cluster_data.columns else round(avg_aqi * 1.5, 1),
                "risk_level": risk,
                "dominant_pollutant": cluster_data["dominant_pollutant"].mode().iloc[0] if "dominant_pollutant" in cluster_data.columns and not cluster_data.empty else "PM2.5",
                "cities": list(cluster_data["city"].unique()) if "city" in cluster_data.columns else [],
            })

        return clusters

    def _calc_radius(self, data: pd.DataFrame) -> float:
        """Calculate approximate cluster radius in km."""
        if len(data) < 2:
            return 1.0
        lat_range = data["latitude"].max() - data["latitude"].min()
        lng_range = data["longitude"].max() - data["longitude"].min()
        return max(0.5, (lat_range + lng_range) * 55.5)  # Rough km conversion

    def _merge_hotspots(self, kmeans_clusters: list, dbscan_clusters: list) -> list:
        """Merge and deduplicate hotspots from both algorithms."""
        all_clusters = kmeans_clusters + dbscan_clusters
        # Sort by risk level severity
        risk_order = {"severe": 0, "high_risk": 1, "moderate_risk": 2, "low_risk": 3, "safe": 4}
        all_clusters.sort(key=lambda c: risk_order.get(c["risk_level"], 5))
        return all_clusters[:10]  # Top 10 hotspots

    def _simulated_clusters(self, n_clusters: int = 6) -> dict:
        """Generate simulated cluster data for demo."""
        hotspots = [
            {"name": "Delhi NCR Industrial Belt", "lat": 28.65, "lng": 77.28, "aqi": 280, "risk": "severe", "type": "industrial"},
            {"name": "Mumbai Western Express", "lat": 19.12, "lng": 72.85, "aqi": 165, "risk": "high_risk", "type": "traffic"},
            {"name": "Kolkata Port Area", "lat": 22.55, "lng": 88.33, "aqi": 195, "risk": "high_risk", "type": "industrial"},
            {"name": "Lucknow Old City", "lat": 26.85, "lng": 80.95, "aqi": 220, "risk": "severe", "type": "pollution"},
            {"name": "Pune Industrial Zone", "lat": 18.52, "lng": 73.90, "aqi": 130, "risk": "moderate_risk", "type": "industrial"},
            {"name": "Chennai Harbour", "lat": 13.10, "lng": 80.30, "aqi": 110, "risk": "moderate_risk", "type": "traffic"},
            {"name": "Hyderabad HITEC City", "lat": 17.45, "lng": 78.38, "aqi": 85, "risk": "low_risk", "type": "urban"},
            {"name": "Bangalore Whitefield", "lat": 12.97, "lng": 77.75, "aqi": 75, "risk": "low_risk", "type": "urban"},
        ]

        clusters = []
        for i, h in enumerate(hotspots[:n_clusters]):
            clusters.append({
                "cluster_id": i,
                "algorithm": "kmeans",
                "cluster_type": h["type"],
                "centroid_lat": h["lat"] + random.uniform(-0.02, 0.02),
                "centroid_lng": h["lng"] + random.uniform(-0.02, 0.02),
                "radius_km": round(random.uniform(2, 15), 1),
                "num_points": random.randint(50, 500),
                "avg_aqi": h["aqi"],
                "max_aqi": round(h["aqi"] * random.uniform(1.1, 1.5)),
                "risk_level": h["risk"],
                "dominant_pollutant": random.choice(["PM2.5", "PM10", "NO2", "CO"]),
                "name": h["name"],
                "cities": [h["name"].split(" ")[0]],
            })

        return {
            "algorithm": "combined",
            "n_clusters": len(clusters),
            "clusters": clusters,
            "heatmap_data": self._generate_heatmap_data(),
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_heatmap_data(self) -> list:
        """Generate heatmap-ready data points."""
        points = []
        cities = [
            (28.61, 77.21, "Delhi"), (19.08, 72.88, "Mumbai"),
            (12.97, 77.59, "Bangalore"), (22.57, 88.36, "Kolkata"),
            (13.08, 80.27, "Chennai"), (17.39, 78.49, "Hyderabad"),
        ]

        for lat, lng, city in cities:
            for _ in range(random.randint(20, 60)):
                intensity = random.uniform(0.2, 1.0)
                points.append({
                    "lat": round(lat + random.uniform(-0.15, 0.15), 6),
                    "lng": round(lng + random.uniform(-0.15, 0.15), 6),
                    "intensity": round(intensity, 3),
                    "aqi": round(intensity * 300 + random.uniform(-20, 20)),
                })

        return points

    def get_geojson(self) -> dict:
        """Export clusters as GeoJSON for map overlays."""
        features = []
        clusters = self.clusters if self.clusters else self._simulated_clusters(6).get("clusters", [])

        for cluster in clusters:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [cluster["centroid_lng"], cluster["centroid_lat"]]
                },
                "properties": {
                    "cluster_id": cluster.get("cluster_id", 0),
                    "risk_level": cluster.get("risk_level", "moderate_risk"),
                    "avg_aqi": cluster.get("avg_aqi", 100),
                    "radius_km": cluster.get("radius_km", 5),
                    "name": cluster.get("name", f"Cluster {cluster.get('cluster_id', 0)}"),
                }
            })

        return {"type": "FeatureCollection", "features": features}


# Singleton instance
hotspot_detector = HotspotDetector()
