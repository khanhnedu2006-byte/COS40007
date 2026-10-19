"""Step 3d. Run cross-validation, then train the final models and save them for the backend.

Output: models/metrics.json, models/cv_results.csv, models/model_bundle.joblib
        bundle = {"hybrid", "conformal", "secondary": {"upload_mbps", "latency_ms"},
                  "latest_quarter_index", "feature_columns"}

Run:    python -m ml.train            (with cross-validation)
        python -m ml.train --skip-cv  (final models only)
"""
import pandas as pd

from ml import config


def train_secondary(data: pd.DataFrame, target: str):
    """XGBoost for upload_mbps or latency_ms on the same features (no physics model yet)."""
    # TODO
    raise NotImplementedError


def train_final(data: pd.DataFrame) -> dict:
    """Train the hybrid model, calibrate the conformal range, train secondary models, return the bundle."""
    # TODO
    raise NotImplementedError


def main() -> None:
    # TODO: đọc config.TRAIN_FILE -> cross_validate -> lưu metrics -> train_final -> joblib.dump
    raise NotImplementedError


if __name__ == "__main__":
    main()
