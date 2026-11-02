"""Build the training tables: cleaned Ookla + tower features.   Owner: Person 1

Outputs (columns in docs/data_contract.md):
- data/processed/hanoi_train.csv  one row per tile and quarter
- data/processed/hanoi_tiles.csv  one row per tile, speeds pooled over the latest quarters (less noisy)
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


TILE_COLUMNS = [
    "quadkey", "latitude", "longitude", "first_quarter", "last_quarter", "quarters",
    "download_mbps", "upload_mbps", "latency_ms", "tests", "devices", "reliability",
    "dist_nearest_tower_m", "towers_500m", "towers_1km", "theory_mbps",
    config.WEIGHT_COLUMN, config.GROUP_COLUMN, "quality_level",
]


def reliability(tests: int) -> str:
    return next(name for upper, name in config.RELIABILITY_LEVELS if tests < upper)


def _weighted_log_mean(values: pd.Series, weights: pd.Series) -> float:
    # Trung bình log có trọng số theo số test: ít bị kéo bởi vài ô cực nhanh/chậm
    return float(np.expm1(np.average(np.log1p(values.clip(lower=0)), weights=weights)))


def build_tile_table(ookla_clean: pd.DataFrame, towers: pd.DataFrame,
                     n_quarters: int = config.POOL_QUARTERS) -> pd.DataFrame:
    """One row per tile: speeds pooled over the latest n_quarters, weighted by the number of tests."""
    latest = sorted(ookla_clean["quarter_index"].unique())[-n_quarters:]
    recent = ookla_clean[ookla_clean["quarter_index"].isin(latest)]

    rows = []
    for quadkey, t in recent.groupby("quadkey"):
        rows.append({
            "quadkey": quadkey,
            "latitude": t["latitude"].iloc[0],
            "longitude": t["longitude"].iloc[0],
            "first_quarter": t.loc[t["quarter_index"].idxmin(), "quarter"],
            "last_quarter": t.loc[t["quarter_index"].idxmax(), "quarter"],
            "quarters": t["quarter"].nunique(),
            "download_mbps": round(_weighted_log_mean(t["download_mbps"], t["tests"]), 2),
            "upload_mbps": round(_weighted_log_mean(t["upload_mbps"], t["tests"]), 2),
            "latency_ms": round(float(np.average(t["latency_ms"], weights=t["tests"])), 1),
            "tests": int(t["tests"].sum()),
            "devices": int(t["devices"].sum()),
        })
    tiles = pd.DataFrame(rows)

    feats = tower_features(tiles["latitude"].to_numpy(), tiles["longitude"].to_numpy(), TowerIndex(towers))
    tiles = pd.concat([tiles, feats.drop(columns=["latitude", "longitude"])], axis=1)
    tiles["reliability"] = tiles["tests"].map(reliability)
    tiles[config.WEIGHT_COLUMN] = np.sqrt(tiles["tests"]).round(3)
    tiles[config.GROUP_COLUMN] = spatial_block_id(tiles["latitude"], tiles["longitude"])
    tiles["quality_level"] = tiles[config.TARGET_COLUMN].map(config.quality_level)
    return tiles[TILE_COLUMNS].reset_index(drop=True)
