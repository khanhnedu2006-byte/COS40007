"""Step 2c. Build the Hanoi training table: cleaned Ookla tiles + tower features.

Input:  data/raw/ookla_hanoi_mobile.csv, data/processed/hanoi_towers.csv
Output: data/processed/hanoi_train.csv
        = Ookla columns + config.FEATURE_COLUMNS + sample_weight, block_id, quality_level

Run:    python -m ml.build_train
"""
import pandas as pd

from ml import config


def quarter_index(quarter: str) -> int:
    """Turn "2025-4" into an increasing integer (e.g. year*4 + quarter - 1)."""
    # TODO
    raise NotImplementedError


def clean_ookla(df: pd.DataFrame) -> pd.DataFrame:
    """Drop missing values, latency > config.MAX_LATENCY_MS, and extreme download in low-test tiles."""
    # TODO
    raise NotImplementedError


def build(ookla: pd.DataFrame, towers: pd.DataFrame) -> pd.DataFrame:
    """Clean tiles, compute tower features once per unique tile, then add
    quarter_index, sample_weight (e.g. sqrt(tests)), block_id and quality_level."""
    # TODO
    raise NotImplementedError


def main() -> None:
    # TODO: đọc file (quadkey dạng str) -> build -> lưu config.TRAIN_FILE
    raise NotImplementedError


if __name__ == "__main__":
    main()
