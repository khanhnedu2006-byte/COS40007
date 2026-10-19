"""Prediction for one clicked point, used by the backend.   Owner: Person 3

Loads the saved bundle with speedmap.artifacts.load_model("hybrid") and the tower table once.
Must compute features with speedmap.features.tower_features.tower_features (same as training)
and set quarter_index to the latest quarter stored in the bundle.

Output keys (docs/api_contract.md):
    latitude, longitude, download_mbps, download_low, download_high, upload_mbps, latency_ms,
    quality_level, theory_mbps, local_effect_mbps, nearest_towers[{radio, operator, latitude, longitude, distance_m}]
"""
from speedmap import config


class Predictor:
    def __init__(self, model_name: str = "hybrid", run_id: str | None = None):
        # TODO: bundle, metadata = load_model(model_name, run_id); towers = load_towers(); index = TowerIndex(towers)
        raise NotImplementedError

    def predict(self, lat: float, lon: float) -> dict:
        # TODO
        raise NotImplementedError

    def tower_list(self) -> list:
        """[{radio, latitude, longitude}, ...] for the map nodes."""
        # TODO
        raise NotImplementedError
