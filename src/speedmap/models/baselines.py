"""Baseline models.   Owner: Person 2

Baseline 1, KNN: location only (latitude, longitude in radians, metric="haversine").
Baseline 2, Random Forest: same features as the main model EXCEPT theory_mbps (no physics).
"""
from speedmap import config
from speedmap.models.base import BaseSpeedModel


class KNNBaseline(BaseSpeedModel):
    name = "knn"

    def __init__(self, n_neighbors: int = 10):
        self.n_neighbors = n_neighbors
        # TODO: sklearn KNeighborsRegressor(weights="distance", metric="haversine")

    def fit(self, X, y, sample_weight=None):
        # TODO
        raise NotImplementedError

    def predict(self, X):
        # TODO
        raise NotImplementedError

    def get_params(self):
        return {"n_neighbors": self.n_neighbors}


class RandomForestBaseline(BaseSpeedModel):
    name = "random_forest"

    def __init__(self, n_estimators: int = 300, min_samples_leaf: int = 5):
        self.n_estimators = n_estimators
        self.min_samples_leaf = min_samples_leaf
        self.columns = [c for c in config.FEATURE_COLUMNS if c != "theory_mbps"]
        # TODO: sklearn RandomForestRegressor(random_state=config.RANDOM_SEED)

    def fit(self, X, y, sample_weight=None):
        # TODO
        raise NotImplementedError

    def predict(self, X):
        # TODO
        raise NotImplementedError

    def get_params(self):
        return {"n_estimators": self.n_estimators, "min_samples_leaf": self.min_samples_leaf}
