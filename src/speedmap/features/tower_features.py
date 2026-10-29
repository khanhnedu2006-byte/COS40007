"""Tower features for any list of points. SHARED by training and the backend.   Owner: Person 1

Output columns (must match config.FEATURE_COLUMNS except quarter_index):
    latitude, longitude, dist_nearest_tower_m, towers_500m, towers_1km, theory_mbps
dist_nearest_tower_m is the true distance to the nearest tower (not capped), because distance
matters a lot in the suburbs. Towers within config.TOWER_SEARCH_RADIUS_M are used for theory_mbps.
"""
import warnings

import numpy as np
import pandas as pd

from speedmap import config
from speedmap.features.spatial import TowerIndex
from speedmap.physics.link_budget import theoretical_speed_mbps


def theory_for_points(lat: np.ndarray, lon: np.ndarray, index: TowerIndex) -> np.ndarray:
    """3GPP theoretical speed for each point from the towers within the search radius.

    Trả về NaN nếu module vật lý (Person 2) chưa viết xong, để phần dữ liệu không bị chặn.
    """
    _, dists = index.query_radius(lat, lon, config.TOWER_SEARCH_RADIUS_M)
    try:
        return np.array([theoretical_speed_mbps(d) for d in dists], dtype=float)
    except NotImplementedError:
        warnings.warn("physics.link_budget is not implemented yet: theory_mbps is NaN")
        return np.full(len(dists), np.nan)


def tower_features(lat: np.ndarray, lon: np.ndarray, index: TowerIndex) -> pd.DataFrame:
    """Compute all tower features for many points."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    feats = pd.DataFrame({
        "latitude": lat,
        "longitude": lon,
        "dist_nearest_tower_m": np.round(index.nearest_distance(lat, lon), 1),
        "towers_500m": index.count_within(lat, lon, 500),
        "towers_1km": index.count_within(lat, lon, 1000),
        "theory_mbps": theory_for_points(lat, lon, index),
    })
    return feats[[c for c in config.FEATURE_COLUMNS if c != "quarter_index"]]
