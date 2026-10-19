"""Run: pytest tests/test_features.py   (Person 1)"""
import numpy as np
import pandas as pd

from speedmap import config
from speedmap.features.spatial import TowerIndex
from speedmap.features.tower_features import tower_features

TOWERS = pd.DataFrame({
    "radio": ["NR", "LTE", "LTE"],
    "operator": [1, 2, 4],
    "latitude": [21.0285, 21.0300, 21.1000],
    "longitude": [105.8542, 105.8560, 105.9000],
})


def test_columns_match_contract():
    feats = tower_features(np.array([21.0285]), np.array([105.8542]), TowerIndex(TOWERS))
    expected = [c for c in config.FEATURE_COLUMNS if c != "quarter_index"]
    assert list(feats.columns) == expected


def test_nearest_distance_is_small_next_to_tower():
    feats = tower_features(np.array([21.0285]), np.array([105.8542]), TowerIndex(TOWERS))
    assert feats["dist_nearest_tower_m"].iloc[0] < 5


def test_far_point_uses_search_radius():
    feats = tower_features(np.array([20.6]), np.array([105.3]), TowerIndex(TOWERS))
    assert feats["dist_nearest_tower_m"].iloc[0] == config.TOWER_SEARCH_RADIUS_M
