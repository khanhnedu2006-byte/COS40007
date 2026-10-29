"""OpenCelliD towers for Hanoi.   Owner: Person 1

4G (LTE) and 5G (NR) cells are merged into one "tower" table: in Vietnam 5G mostly shares sites with 4G,
and OpenCelliD records very few NR cells, so the project does not separate the two technologies.

Input:  data/raw/452.csv.gz (Vietnam, from opencellid.org)
Output: data/interim/hanoi_towers.csv with columns tower_id, latitude, longitude, cells, operators, samples
"""
import pandas as pd

from speedmap import config

OPENCELLID_COLUMNS = [
    "radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
    "range", "samples", "changeable", "created", "updated", "averageSignal",
]


def load_opencellid(path=config.OPENCELLID_RAW_FILE) -> pd.DataFrame:
    """Read the raw file (with or without a header row)."""
    df = pd.read_csv(path, header=None, names=OPENCELLID_COLUMNS, low_memory=False)
    df = df[df["radio"] != "radio"]  # bỏ dòng header nếu file có
    num_cols = ["mcc", "net", "lon", "lat", "range", "samples"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def filter_hanoi(df: pd.DataFrame) -> pd.DataFrame:
    """Keep 4G/5G cells inside Hanoi with enough samples, then merge cells at the same place into towers."""
    b = config.HANOI_BBOX
    cells = df[
        df["radio"].isin(config.TOWER_RADIOS)
        & df["lat"].between(b["lat_min"], b["lat_max"])
        & df["lon"].between(b["lon_min"], b["lon_max"])
        & (df["samples"] >= config.MIN_TOWER_SAMPLES)
    ].drop_duplicates(subset=["mcc", "net", "area", "cell"])

    # Các cell cách nhau dưới ~100 m được coi là cùng một trạm
    d = config.TOWER_MERGE_DECIMALS
    key = cells["lat"].round(d).astype(str) + "_" + cells["lon"].round(d).astype(str)
    towers = (
        cells.assign(key=key)
        .groupby("key")
        .agg(
            latitude=("lat", "mean"),
            longitude=("lon", "mean"),
            cells=("cell", "size"),
            operators=("net", lambda s: ",".join(str(int(v)) for v in sorted(s.unique()))),
            samples=("samples", "sum"),
        )
        .reset_index(drop=True)
    )
    towers[["latitude", "longitude"]] = towers[["latitude", "longitude"]].round(6)
    towers.insert(0, "tower_id", range(1, len(towers) + 1))
    return towers


def load_towers(path=config.TOWERS_FILE) -> pd.DataFrame:
    """Load the processed tower table (used by features and by the backend)."""
    return pd.read_csv(path)
