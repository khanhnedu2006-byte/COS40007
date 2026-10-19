"""Common interface for every model so notebooks and evaluation can treat them the same way."""
import numpy as np
import pandas as pd


class BaseSpeedModel:
    name = "base"

    def fit(self, X: pd.DataFrame, y: np.ndarray, sample_weight: np.ndarray | None = None):
        raise NotImplementedError

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

    def get_params(self) -> dict:
        """Hyperparameters to store in metadata.json when the model is saved."""
        return {}
