"""Step 2b. Feature engineering SHARED by training and the backend.

Important: training tiles and clicked map points must go through the same functions,
otherwise the model receives different inputs at prediction time.

Output columns must match config.FEATURE_COLUMNS (quarter_index is added by the caller).
"""
import numpy as np
import pandas as pd

from ml import config

EARTH_RADIUS_M = 6_371_000


class TowerIndex:
    """Spatial index over tower locations (hint: sklearn BallTree with metric="haversine", coordinates in radians)."""

    def __init__(self, towers: pd.DataFrame):
        self.towers = towers.reset_index(drop=True)
        # TODO: tạo BallTree từ latitude, longitude

    def query_radius(self, lat: np.ndarray, lon: np.ndarray, radius_m: float):
        """Return, for each point, the tower indices and distances (metres) within radius_m."""
        # TODO
        raise NotImplementedError

    def nearest(self, lat: float, lon: float, k: int) -> pd.DataFrame:
        """Return the k nearest towers to one point with a distance_m column (for the map popup)."""
        # TODO
        raise NotImplementedError


def tower_features(lat: np.ndarray, lon: np.ndarray, index: TowerIndex) -> pd.DataFrame:
    """Compute tower features for many points.

    Columns: latitude, longitude, dist_nearest_tower_m, dist_nearest_nr_m,
             towers_500m, towers_1km, nr_share_1km, theory_mbps
    Search radius: config.TOWER_SEARCH_RADIUS_M (if no tower, use the radius as distance).
    """
    # TODO: query_radius -> tính từng đặc trưng -> gọi physics_3gpp.best_theoretical_speed
    raise NotImplementedError


def spatial_block_id(lat: np.ndarray, lon: np.ndarray, block_km: float = config.SPATIAL_BLOCK_KM) -> np.ndarray:
    """Assign each point to a block of block_km x block_km, used as groups for spatial cross-validation."""
    # TODO
    raise NotImplementedError
