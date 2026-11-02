"""OpenCelliD towers for Hanoi.   Owner: Person 1

All mobile cells (LTE and NR) are merged into one "tower" table: the project predicts mobile internet
speed in general, so it does not separate network technologies.

Input:  data/raw/452.csv.gz (Vietnam, from opencellid.org)
Optional input: data/raw/osm_comm_towers.csv (OpenStreetMap telecom masts, fills gaps in the suburbs)
Output: data/interim/hanoi_towers.csv with columns tower_id, latitude, longitude, cells, operators, samples, inside_hanoi, source
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from speedmap import config
from speedmap.data import boundary

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
    """Keep mobile cells inside Hanoi (or within TOWER_BUFFER_KM of the border) with enough samples,
    then merge cells at the same place into towers."""
    b = config.HANOI_BBOX
    margin = config.TOWER_BUFFER_KM / 100  # ~1 độ = 100 km, lọc thô trước khi xét ranh giới
    cells = df[
        df["radio"].isin(config.TOWER_RADIOS)
        & df["lat"].between(b["lat_min"] - margin, b["lat_max"] + margin)
        & df["lon"].between(b["lon_min"] - margin, b["lon_max"] + margin)
        & (df["samples"] >= config.MIN_TOWER_SAMPLES)
    ].drop_duplicates(subset=["mcc", "net", "area", "cell"])
    cells = cells[boundary.inside_or_near(cells["lat"].to_numpy(), cells["lon"].to_numpy(), config.TOWER_BUFFER_KM)]

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
    towers["inside_hanoi"] = boundary.contains(towers["latitude"].to_numpy(), towers["longitude"].to_numpy())
    return towers


def load_osm_masts(path=config.OSM_TOWERS_RAW_FILE) -> pd.DataFrame:
    """Telecom masts from OpenStreetMap (scripts/fetch_osm_towers.py), inside Hanoi or near the border.

    Bỏ trung tâm dữ liệu, tháp chùa, cột đèn...: chỉ giữ cột/tháp viễn thông.
    """
    if not Path(path).exists():
        return pd.DataFrame(columns=["latitude", "longitude"])
    osm = pd.read_csv(path)
    tags = osm["tags"].map(json.loads)
    is_mast = tags.map(lambda t: t.get("man_made") in ("mast", "tower", "communications_tower"))
    is_telecom = tags.map(lambda t: t.get("tower:type") == "communication" or t.get("man_made") == "communications_tower")
    osm = osm[is_mast & is_telecom]
    near = boundary.inside_or_near(osm["latitude"].to_numpy(), osm["longitude"].to_numpy(), config.TOWER_BUFFER_KM)
    return osm[near][["latitude", "longitude"]].reset_index(drop=True)


def add_osm_masts(towers: pd.DataFrame, osm: pd.DataFrame, min_gap_m: float = config.OSM_MIN_GAP_M) -> pd.DataFrame:
    """Append OSM masts that are not already close to an OpenCelliD tower (source column tells them apart)."""
    towers = towers.assign(source="opencellid")
    if osm.empty:
        return towers
    tree = BallTree(np.radians(towers[["latitude", "longitude"]].to_numpy()), metric="haversine")
    dist, _ = tree.query(np.radians(osm[["latitude", "longitude"]].to_numpy()), k=1)
    new = osm[dist[:, 0] * 6_371_000 > min_gap_m].copy()
    new["tower_id"] = range(int(towers["tower_id"].max()) + 1, int(towers["tower_id"].max()) + 1 + len(new))
    new["cells"], new["operators"], new["samples"] = 0, "", 0
    new["inside_hanoi"] = boundary.contains(new["latitude"].to_numpy(), new["longitude"].to_numpy())
    new["source"] = "osm"
    return pd.concat([towers, new[towers.columns]], ignore_index=True)


def load_towers(path=config.TOWERS_FILE) -> pd.DataFrame:
    """Load the processed tower table (used by features and by the backend)."""
    return pd.read_csv(path)
