"""Hanoi administrative boundary: point-in-polygon and distance to the border.   Owner: Person 1

Polygon: data/reference/hanoi_boundary.geojson (geoBoundaries gbOpen, CC BY 4.0).
Used by data cleaning (keep tiles inside Hanoi), tower filtering (keep towers inside Hanoi
or within config.TOWER_BUFFER_KM of the border) and the backend (reject clicks outside Hanoi).
"""
import json
from functools import lru_cache

import numpy as np
from matplotlib.path import Path as PolygonPath
from sklearn.neighbors import BallTree

from speedmap import config

EARTH_RADIUS_M = 6_371_000
BORDER_STEP_M = 100  # chia nhỏ cạnh biên để tính khoảng cách tới biên


@lru_cache(maxsize=1)
def _rings() -> list:
    geo = json.loads(config.HANOI_BOUNDARY_FILE.read_text(encoding="utf-8"))
    geom = geo["features"][0]["geometry"]
    polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [np.asarray(ring, dtype=float) for poly in polygons for ring in poly]  # (lon, lat)


@lru_cache(maxsize=1)
def _paths() -> list:
    return [PolygonPath(ring) for ring in _rings()]


@lru_cache(maxsize=1)
def _border_tree() -> BallTree:
    pts = []
    for ring in _rings():
        for (lon1, lat1), (lon2, lat2) in zip(ring[:-1], ring[1:]):
            seg_m = np.hypot((lat2 - lat1) * 110_570, (lon2 - lon1) * 111_320 * np.cos(np.radians(lat1)))
            n = max(int(seg_m // BORDER_STEP_M), 1)
            t = np.linspace(0, 1, n, endpoint=False)
            pts.append(np.column_stack([lat1 + t * (lat2 - lat1), lon1 + t * (lon2 - lon1)]))
    return BallTree(np.radians(np.vstack(pts)), metric="haversine")


def contains(lat, lon) -> np.ndarray:
    """True for points inside Hanoi (holes are handled by even-odd counting over all rings)."""
    pts = np.column_stack([np.atleast_1d(lon), np.atleast_1d(lat)]).astype(float)
    inside = np.zeros(len(pts), dtype=bool)
    for path in _paths():
        inside ^= path.contains_points(pts)
    return inside


def distance_to_border_m(lat, lon) -> np.ndarray:
    pts = np.radians(np.column_stack([np.atleast_1d(lat), np.atleast_1d(lon)]).astype(float))
    dist, _ = _border_tree().query(pts, k=1)
    return dist[:, 0] * EARTH_RADIUS_M


def inside_or_near(lat, lon, buffer_km: float) -> np.ndarray:
    """Inside Hanoi, or outside but within buffer_km of the border."""
    return contains(lat, lon) | (distance_to_border_m(lat, lon) <= buffer_km * 1000)
