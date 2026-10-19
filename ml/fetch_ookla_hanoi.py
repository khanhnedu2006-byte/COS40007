"""Download Ookla Open Data mobile tiles for Hanoi only.

Reads the global parquet files directly from Ookla's public S3 bucket with DuckDB,
keeping only tiles inside the Hanoi bounding box, so the full global file is never downloaded.

Usage:
    pip install duckdb pandas
    python ml/fetch_ookla_hanoi.py
    python ml/fetch_ookla_hanoi.py --quarters 2025-4 2026-1 --out data/raw/ookla_hanoi_mobile.csv
"""
import argparse
import math
from pathlib import Path

import duckdb
import pandas as pd

# Khung bao gần đúng toàn thành phố Hà Nội (gồm cả ngoại thành)
HANOI_BBOX = {"lat_min": 20.53, "lat_max": 21.40, "lon_min": 105.28, "lon_max": 106.03}

DEFAULT_QUARTERS = ["2024-4", "2025-1", "2025-2", "2025-3", "2025-4", "2026-1"]
BASE_URL = "https://ookla-open-data.s3.amazonaws.com/parquet/performance/type={kind}/year={year}/quarter={q}/{date}_performance_{kind}_tiles.parquet"
TILE_ZOOM = 16
PREFIX_ZOOM = 10


def latlon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def tile_to_quadkey(x: int, y: int, zoom: int) -> str:
    digits = []
    for i in range(zoom, 0, -1):
        mask = 1 << (i - 1)
        digit = (1 if x & mask else 0) + (2 if y & mask else 0)
        digits.append(str(digit))
    return "".join(digits)


def quadkey_to_center(quadkey: str) -> tuple[float, float]:
    x = y = 0
    zoom = len(quadkey)
    for i, ch in enumerate(quadkey):
        mask = 1 << (zoom - i - 1)
        d = int(ch)
        if d & 1:
            x |= mask
        if d & 2:
            y |= mask
    n = 2 ** zoom
    lon = (x + 0.5) / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 0.5) / n))))
    return lat, lon


def bbox_prefixes(bbox: dict, zoom: int) -> list[str]:
    x0, y0 = latlon_to_tile(bbox["lat_max"], bbox["lon_min"], zoom)
    x1, y1 = latlon_to_tile(bbox["lat_min"], bbox["lon_max"], zoom)
    return [tile_to_quadkey(x, y, zoom) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def quarter_url(quarter: str, kind: str) -> str:
    year, q = quarter.split("-")
    month = {"1": "01", "2": "04", "3": "07", "4": "10"}[q]
    return BASE_URL.format(kind=kind, year=year, q=q, date=f"{year}-{month}-01")


def fetch_quarter(con: duckdb.DuckDBPyConnection, source: str, prefixes: list[str]) -> pd.DataFrame:
    # Lọc theo tiền tố quadkey để DuckDB chỉ đọc phần dữ liệu quanh Hà Nội
    prefix_filter = " OR ".join(f"starts_with(quadkey, '{p}')" for p in prefixes)
    query = f"""
        SELECT quadkey, avg_d_kbps, avg_u_kbps, avg_lat_ms, tests, devices
        FROM read_parquet('{source}')
        WHERE {prefix_filter}
    """
    return con.execute(query).df()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarters", nargs="+", default=DEFAULT_QUARTERS, help="e.g. 2025-4 2026-1")
    parser.add_argument("--kind", default="mobile", choices=["mobile", "fixed"])
    parser.add_argument("--out", type=Path, default=Path("data/raw/ookla_hanoi_mobile.csv"))
    parser.add_argument("--source-template", default=None, help="Local parquet path with {quarter} placeholder, for offline testing")
    args = parser.parse_args()

    con = duckdb.connect()
    if args.source_template is None:
        con.execute("INSTALL httpfs; LOAD httpfs;")

    prefixes = bbox_prefixes(HANOI_BBOX, PREFIX_ZOOM)
    frames = []
    for quarter in args.quarters:
        source = args.source_template.format(quarter=quarter) if args.source_template else quarter_url(quarter, args.kind)
        print(f"Reading {quarter} ...", flush=True)
        try:
            df = fetch_quarter(con, source, prefixes)
        except Exception as exc:
            print(f"  skipped {quarter}: {exc}")
            continue
        df["quarter"] = quarter
        frames.append(df)
        print(f"  {len(df):,} tiles near Hanoi")

    if not frames:
        raise SystemExit("No data downloaded")

    data = pd.concat(frames, ignore_index=True)
    centers = data["quadkey"].astype(str).map(quadkey_to_center)
    data["latitude"] = centers.map(lambda c: round(c[0], 6))
    data["longitude"] = centers.map(lambda c: round(c[1], 6))

    inside = data["latitude"].between(HANOI_BBOX["lat_min"], HANOI_BBOX["lat_max"]) & data["longitude"].between(
        HANOI_BBOX["lon_min"], HANOI_BBOX["lon_max"]
    )
    data = data[inside].copy()

    data["download_mbps"] = (data["avg_d_kbps"] / 1000).round(2)
    data["upload_mbps"] = (data["avg_u_kbps"] / 1000).round(2)
    data = data.rename(columns={"avg_lat_ms": "latency_ms"})
    data = data[["quarter", "quadkey", "latitude", "longitude", "download_mbps", "upload_mbps", "latency_ms", "tests", "devices"]]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.out, index=False)
    print(f"Wrote {len(data):,} rows ({data['quadkey'].nunique():,} unique tiles) to {args.out}")


if __name__ == "__main__":
    main()
