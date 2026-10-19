"""Spatial helpers: tower index, distances, blocks for cross-validation.   Owner: Person 1"""
import numpy as np
import pandas as pd

from speedmap import config

EARTH_RADIUS_M = 6_371_000


class TowerIndex:
    """Fast distance queries over tower locations.

    Gợi ý: sklearn.neighbors.BallTree(np.radians(latlon), metric="haversine");
    khoảng cách trả về theo radian, nhân EARTH_RADIUS_M để ra mét.
    """

    def __init__(self, towers: pd.DataFrame):
        self.towers = towers.reset_index(drop=True)
        self.radio = self.towers["radio"].to_numpy()
        # TODO: tạo BallTree

    def query_radius(self, lat: np.ndarray, lon: np.ndarray, radius_m: float):
        """For each point return (tower_indices, distances_m) of towers within radius_m."""
        # TODO
        raise NotImplementedError

    def nearest(self, lat: float, lon: float, k: int) -> pd.DataFrame:
        """k nearest towers to one point, with a distance_m column."""
        # TODO
        raise NotImplementedError


def spatial_block_id(lat, lon, block_km: float = config.SPATIAL_BLOCK_KM) -> np.ndarray:
    """Integer id of the block_km x block_km square containing each point (groups for spatial CV)."""
    # TODO
    raise NotImplementedError
