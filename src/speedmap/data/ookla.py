"""Ookla mobile tiles for Hanoi: load, clean, add time index.   Owner: Person 1

Raw file columns: quarter, quadkey, latitude, longitude, download_mbps, upload_mbps,
latency_ms, tests, devices (created by scripts/fetch_ookla_hanoi.py).
"""
import math

import pandas as pd

from speedmap import config
from speedmap.data import boundary

TILE_ZOOM = 16  # ô Ookla là tile zoom 16 (khoảng 610 m)


def tile_quadkey(lat: float, lon: float, zoom: int = TILE_ZOOM) -> str:
    """Quadkey of the map tile containing a point."""
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    digits = []
    for i in range(zoom, 0, -1):
        mask = 1 << (i - 1)
        digits.append(str((1 if x & mask else 0) + (2 if y & mask else 0)))
    return "".join(digits)


def load_raw(path=config.OOKLA_RAW_FILE) -> pd.DataFrame:
    """Read the raw Ookla CSV.

    quadkey is rebuilt from the tile centre, because opening the CSV in Excel turns it into
    a number like 1.3221E+15 and loses the tile id.
    """
    df = pd.read_csv(path)
    df["quadkey"] = [tile_quadkey(a, b) for a, b in zip(df["latitude"], df["longitude"])]
    return df


def quarter_index(quarter: str) -> int:
    """Convert "2025-4" to an increasing integer: year * 4 + quarter - 1."""
    year, q = str(quarter).split("-")
    return int(year) * 4 + int(q) - 1


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy.

    Rules (values in config):
    - keep only tiles inside the Hanoi administrative boundary
    - drop rows with missing download, latitude or longitude, or download <= 0
    - drop latency > MAX_LATENCY_MS
    - drop extreme download (above the 99.5th percentile) in tiles with tests < MIN_TESTS_FOR_EVAL
    - add column quarter_index
    """
    out = df.dropna(subset=["download_mbps", "latitude", "longitude"]).copy()
    out = out[out["download_mbps"] > 0]
    out = out[boundary.contains(out["latitude"].to_numpy(), out["longitude"].to_numpy())]
    out = out[out["latency_ms"].isna() | (out["latency_ms"] <= config.MAX_LATENCY_MS)]
    # Ô có ít test dễ nhiễu: bỏ giá trị download cực lớn ở các ô này
    limit = out["download_mbps"].quantile(0.995)
    out = out[~((out["tests"] < config.MIN_TESTS_FOR_EVAL) & (out["download_mbps"] > limit))]
    out["quarter_index"] = out["quarter"].map(quarter_index)
    return out.reset_index(drop=True)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-quarter summary for the report: tiles, total tests, median download/upload/latency."""
    return (
        df.groupby("quarter")
        .agg(
            tiles=("quadkey", "nunique"),
            tests=("tests", "sum"),
            median_download=("download_mbps", "median"),
            median_upload=("upload_mbps", "median"),
            median_latency=("latency_ms", "median"),
        )
        .round(1)
    )
