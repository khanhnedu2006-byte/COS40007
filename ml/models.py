"""Step 3b. Models. Every model exposes fit(X, y, sample_weight=None) and predict(X).

- KNNBaseline:          Baseline 1, location only
- RandomForestBaseline: Baseline 2, same features as the main model but without theory_mbps
- HybridModel:          Main model, 3GPP theoretical speed + XGBoost correction
- PhysicsOnly, XGBoostOnly: only for the ablation study
- ConformalInterval:    80% confidence range around the main model
"""
import numpy as np
import pandas as pd

from ml import config


class KNNBaseline:
    name = "knn"

    def fit(self, X: pd.DataFrame, y: np.ndarray, sample_weight=None):
        # TODO: KNeighborsRegressor trên latitude, longitude (radians, metric="haversine")
        raise NotImplementedError

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class RandomForestBaseline:
    name = "random_forest"

    def fit(self, X: pd.DataFrame, y: np.ndarray, sample_weight=None):
        # TODO: RandomForestRegressor trên config.FEATURE_COLUMNS trừ theory_mbps
        raise NotImplementedError

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class HybridModel:
    """predicted = theoretical speed corrected by XGBoost.

    Suggested target: log1p(real) - log1p(theory_mbps); prediction = expm1(log1p(theory) + correction).
    """

    name = "hybrid"

    def fit(self, X: pd.DataFrame, y: np.ndarray, sample_weight=None):
        # TODO: XGBRegressor trên config.FEATURE_COLUMNS, target là phần chênh lệch
        raise NotImplementedError

    def correction(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class PhysicsOnly:
    name = "physics_only"

    def fit(self, X, y, sample_weight=None):
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return X["theory_mbps"].to_numpy()


class XGBoostOnly:
    name = "xgboost_only"

    def fit(self, X, y, sample_weight=None):
        # TODO: XGBoost trên đặc trưng không có theory_mbps
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError


class ConformalInterval:
    """Split conformal: q = quantile of |y - y_pred| on a calibration set; range = y_pred ± q."""

    def __init__(self, level: float = config.CONFIDENCE_LEVEL):
        self.level = level
        self.q = None

    def calibrate(self, y_true: np.ndarray, y_pred: np.ndarray):
        # TODO: dùng quantile mức ceil((n+1)*level)/n
        raise NotImplementedError

    def interval(self, y_pred: np.ndarray):
        raise NotImplementedError


MODEL_REGISTRY = {
    "knn": KNNBaseline,
    "random_forest": RandomForestBaseline,
    "hybrid": HybridModel,
    "physics_only": PhysicsOnly,
    "xgboost_only": XGBoostOnly,
}
