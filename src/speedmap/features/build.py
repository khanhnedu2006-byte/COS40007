"""Build the training table: cleaned Ookla + tower features (+ optional OSM).   Owner: Person 1

Output: data/processed/hanoi_train.csv, columns described in docs/data_contract.md
"""
import warnings

import numpy as np
import pandas as pd

from speedmap import config
from speedmap.features.spatial import TowerIndex, spatial_block_id
from speedmap.features.tower_features import tower_features

OUTPUT_COLUMNS = [
    "quarter", "quarter_index", "quadkey", "latitude", "longitude",
    "download_mbps", "upload_mbps", "latency_ms", "tests", "devices",
    "dist_nearest_tower_m", "towers_500m", "towers_1km", "theory_mbps",
    config.WEIGHT_COLUMN, config.GROUP_COLUMN, "quality_level",
]


def build_training_table(ookla_clean: pd.DataFrame, towers: pd.DataFrame) -> pd.DataFrame:
    """Cleaned Ookla rows + tower features, sample weight, CV block and quality level."""
    # Mỗi ô lặp lại qua nhiều quý: chỉ tính đặc trưng trạm một lần cho mỗi quadkey
    tiles = ookla_clean.drop_duplicates("quadkey")[["quadkey", "latitude", "longitude"]]
    feats = tower_features(tiles["latitude"].to_numpy(), tiles["longitude"].to_numpy(), TowerIndex(towers))
    feats = feats.drop(columns=["latitude", "longitude"])
    feats.insert(0, "quadkey", tiles["quadkey"].to_numpy())

    df = ookla_clean.merge(feats, on="quadkey", how="left")
    df[config.WEIGHT_COLUMN] = np.sqrt(df["tests"]).round(3)
    df[config.GROUP_COLUMN] = spatial_block_id(df["latitude"], df["longitude"])
    df["quality_level"] = df[config.TARGET_COLUMN].map(config.quality_level)
    df = df[OUTPUT_COLUMNS].sort_values(["quarter_index", "quadkey"]).reset_index(drop=True)
    validate_training_table(df)
    return df


def validate_training_table(df: pd.DataFrame) -> None:
    """Raise an error if required columns are missing or contain invalid values."""
    required = config.FEATURE_COLUMNS + [config.TARGET_COLUMN, config.WEIGHT_COLUMN, config.GROUP_COLUMN, "tests"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    must_be_complete = [c for c in required if c != "theory_mbps"]
    bad = [c for c in must_be_complete if df[c].isna().any()]
    if bad:
        raise ValueError(f"Missing values in: {bad}")
    if (df[config.TARGET_COLUMN] <= 0).any():
        raise ValueError("download_mbps must be positive")
    if df["theory_mbps"].isna().any():
        warnings.warn("theory_mbps is empty: rebuild the table after the physics module is finished")
