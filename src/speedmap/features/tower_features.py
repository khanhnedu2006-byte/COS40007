"""Tower features for any list of points. SHARED by training and the backend.   Owner: Person 1

Output columns (must match config.FEATURE_COLUMNS except quarter_index):
    latitude, longitude, dist_nearest_tower_m, dist_nearest_nr_m,
    towers_500m, towers_1km, nr_share_1km, theory_mbps
If there is no tower within config.TOWER_SEARCH_RADIUS_M, use the radius as the distance.
"""
import numpy as np
import pandas as pd

from speedmap.features.spatial import TowerIndex


def tower_features(lat: np.ndarray, lon: np.ndarray, index: TowerIndex) -> pd.DataFrame:
    """Compute all tower features for many points.

    theory_mbps comes from speedmap.physics.link_budget.best_theoretical_speed
    with the distances to NR and LTE towers of each point.
    """
    # TODO
    raise NotImplementedError
