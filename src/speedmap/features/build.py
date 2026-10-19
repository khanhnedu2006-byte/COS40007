"""Build the training table: cleaned Ookla + tower features (+ optional OSM).   Owner: Person 1

Output: data/processed/hanoi_train.csv, columns described in docs/data_contract.md
"""
import pandas as pd

from speedmap import config


def build_training_table(ookla_clean: pd.DataFrame, towers: pd.DataFrame) -> pd.DataFrame:
    """Steps:
    1. compute tower features once per unique quadkey (tiles repeat across quarters)
    2. merge back onto every tile-quarter row
    3. add sample_weight (e.g. sqrt(tests)), block_id, quality_level
    4. check that every column in config.FEATURE_COLUMNS exists
    """
    # TODO
    raise NotImplementedError


def validate_training_table(df: pd.DataFrame) -> None:
    """Raise an error if required columns are missing or contain invalid values."""
    required = config.FEATURE_COLUMNS + [config.TARGET_COLUMN, config.WEIGHT_COLUMN, config.GROUP_COLUMN, "tests"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
