"""Loads the saved models and tower table once, then predicts for any clicked point."""
from ml import config


class Predictor:
    def __init__(self):
        # TODO: joblib.load(config.MODELS_DIR / "model_bundle.joblib"), load_towers(), TowerIndex(towers)
        raise NotImplementedError

    def predict(self, lat: float, lon: float) -> dict:
        """Return the JSON for one point.

        Dùng đúng ml.features.tower_features như lúc train, thêm quarter_index = quý mới nhất.
        Expected keys: latitude, longitude, download_mbps, download_low, download_high,
        upload_mbps, latency_ms, quality_level, theory_mbps, local_effect_mbps,
        nearest_towers [{radio, operator, latitude, longitude, distance_m}] (config.NEAREST_TOWERS_IN_POPUP)
        """
        raise NotImplementedError

    def tower_list(self) -> list:
        """Return [{radio, latitude, longitude}, ...] for the map nodes."""
        raise NotImplementedError
