"""OpenCelliD towers for Hanoi.   Owner: Person 1

Input:  data/raw/452.csv.gz (Vietnam, from opencellid.org; needs a free account token)
Output: data/interim/hanoi_towers.csv with columns radio, operator, latitude, longitude, range_m, samples
"""
import pandas as pd

from speedmap import config

OPENCELLID_COLUMNS = [
    "radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
    "range", "samples", "changeable", "created", "updated", "averageSignal",
]


def load_opencellid(path=config.OPENCELLID_RAW_FILE) -> pd.DataFrame:
    """Read the raw file. It may or may not have a header row; name the columns with OPENCELLID_COLUMNS."""
    # TODO
    raise NotImplementedError


def filter_hanoi(df: pd.DataFrame) -> pd.DataFrame:
    """Keep config.TOWER_RADIOS inside config.HANOI_BBOX with samples >= MIN_TOWER_SAMPLES; drop duplicates;
    rename lat/lon/net/range to latitude/longitude/operator/range_m."""
    # TODO
    raise NotImplementedError


def load_towers(path=config.TOWERS_FILE) -> pd.DataFrame:
    """Load the processed tower table (used by features and by the backend)."""
    return pd.read_csv(path)
