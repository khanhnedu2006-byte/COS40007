"""Main model: 3GPP theoretical speed + XGBoost correction.   Owner: Person 2

    target     = log1p(real download) - log1p(theory_mbps)
    prediction = expm1(log1p(theory_mbps) + XGBoost(features))

Also two ablation models: PhysicsOnly (3GPP alone) and XGBoostOnly (no theory_mbps).
"""
import numpy as np

from speedmap import config
from speedmap.models.base import BaseSpeedModel

DEFAULT_XGB_PARAMS = dict(
    n_estimators=600, learning_rate=0.03, max_depth=6,
    subsample=0.8, colsample_bytree=0.8, random_state=config.RANDOM_SEED,
)


class HybridModel(BaseSpeedModel):
    name = "hybrid"

    def __init__(self, **xgb_params):
        self.params = {**DEFAULT_XGB_PARAMS, **xgb_params}
        self.columns = list(config.FEATURE_COLUMNS)
        # TODO: xgboost.XGBRegressor(**self.params)

    def fit(self, X, y, sample_weight=None):
        # TODO
        raise NotImplementedError

    def correction(self, X) -> np.ndarray:
        """XGBoost output (log ratio). Positive = faster than theory."""
        # TODO
        raise NotImplementedError

    def predict(self, X):
        # TODO
        raise NotImplementedError

    def get_params(self):
        return self.params


class PhysicsOnly(BaseSpeedModel):
    name = "physics_only"

    def fit(self, X, y, sample_weight=None):
        return self

    def predict(self, X):
        return X["theory_mbps"].to_numpy()


class XGBoostOnly(BaseSpeedModel):
    name = "xgboost_only"

    def __init__(self, **xgb_params):
        self.params = {**DEFAULT_XGB_PARAMS, **xgb_params}
        self.columns = [c for c in config.FEATURE_COLUMNS if c != "theory_mbps"]
        # TODO

    def fit(self, X, y, sample_weight=None):
        # TODO: train on log1p(y)
        raise NotImplementedError

    def predict(self, X):
        # TODO
        raise NotImplementedError

    def get_params(self):
        return self.params
