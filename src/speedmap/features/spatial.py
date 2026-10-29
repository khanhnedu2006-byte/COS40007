"""Spatial helpers: tower index, distances, blocks for cross-validation.   Owner: Person 1"""
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from speedmap import config

EARTH_RADIUS_M = 6_371_000
KM_PER_DEG_LAT = 110.57


def _radians(lat, lon) -> np.ndarray:
    return np.radians(np.column_stack([np.asarray(lat, dtype=float), np.asarray(lon, dtype=float)]))


class TowerIndex:
    """Fast distance queries over tower locations (BallTree with the haversine metric)."""

    def __init__(self, towers: pd.DataFrame):
        self.towers = towers.reset_index(drop=True)
        self.tree = BallTree(_radians(self.towers["latitude"], self.towers["longitude"]), metric="haversine")

    def nearest_distance(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        """Distance in metres from each point to its nearest tower."""
        dist, _ = self.tree.query(_radians(lat, lon), k=1)
        return dist[:, 0] * EARTH_RADIUS_M

    def count_within(self, lat: np.ndarray, lon: np.ndarray, radius_m: float) -> np.ndarray:
        """Number of towers within radius_m of each point."""
        return self.tree.query_radius(_radians(lat, lon), r=radius_m / EARTH_RADIUS_M, count_only=True)

    def query_radius(self, lat: np.ndarray, lon: np.ndarray, radius_m: float):
        """For each point return (tower_indices, distances_m) of towers within radius_m, nearest first."""
        idx, dist = self.tree.query_radius(
            _radians(lat, lon), r=radius_m / EARTH_RADIUS_M, return_distance=True, sort_results=True
        )
        return idx, [d * EARTH_RADIUS_M for d in dist]

    def nearest(self, lat: float, lon: float, k: int) -> pd.DataFrame:
        """k nearest towers to one point, with a distance_m column."""
        k = min(k, len(self.towers))
        dist, idx = self.tree.query(_radians([lat], [lon]), k=k)
        out = self.towers.iloc[idx[0]].copy()
        out["distance_m"] = np.round(dist[0] * EARTH_RADIUS_M).astype(int)
        return out.reset_index(drop=True)


def spatial_block_id(lat, lon, block_km: float = config.SPATIAL_BLOCK_KM) -> np.ndarray:
    """Integer id of the block_km x block_km square containing each point (groups for spatial CV)."""
    lat0, lon0 = config.HANOI_CENTER
    km_per_deg_lon = 111.32 * np.cos(np.radians(lat0))
    ix = np.floor((np.asarray(lon, dtype=float) - lon0) * km_per_deg_lon / block_km).astype(int)
    iy = np.floor((np.asarray(lat, dtype=float) - lat0) * KM_PER_DEG_LAT / block_km).astype(int)
    # Ghép (iy, ix) thành một số nguyên duy nhất
    return (iy + 1000) * 10_000 + (ix + 1000)
