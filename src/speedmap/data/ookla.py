"""Ookla mobile tiles for Hanoi: load, clean, add time index.   Owner: Person 1

Raw file columns: quarter, quadkey, latitude, longitude, download_mbps, upload_mbps,
latency_ms, tests, devices (created by scripts/fetch_ookla_hanoi.py).
"""
import pandas as pd

from speedmap import config


def load_raw(path=config.OOKLA_RAW_FILE) -> pd.DataFrame:
    """Read the raw Ookla CSV; keep quadkey as string."""
    return pd.read_csv(path, dtype={"quadkey": str})


def quarter_index(quarter: str) -> int:
    """Convert "2025-4" to an increasing integer, e.g. year * 4 + quarter - 1."""
    # TODO
    raise NotImplementedError


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy.

    Rules (values in config):
    - drop rows with missing download, latitude or longitude
    - drop latency > MAX_LATENCY_MS
    - drop extreme download (above the 99.5th percentile) in tiles with tests < MIN_TESTS_FOR_EVAL
    - add column quarter_index
    """
    # TODO
    raise NotImplementedError


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-quarter summary for the report: tiles, total tests, median download/upload/latency."""
    # TODO
    raise NotImplementedError
