"""Step 2a. Filter the OpenCelliD Vietnam file (MCC 452) to 4G/5G towers inside Hanoi.

Input:  data/raw/452.csv.gz (download from opencellid.org)
Output: data/processed/hanoi_towers.csv with columns
        radio, operator, latitude, longitude, range_m, samples

Run:    python -m ml.prepare_towers
"""
import pandas as pd

from ml import config


def load_opencellid(path) -> pd.DataFrame:
    """Read the raw OpenCelliD file and return a DataFrame with named columns."""
    # TODO: đọc file, kiểm tra file có dòng tiêu đề hay không, đặt tên cột
    raise NotImplementedError


def filter_hanoi(df: pd.DataFrame) -> pd.DataFrame:
    """Keep LTE and NR towers inside config.HANOI_BBOX with at least config.MIN_TOWER_SAMPLES samples."""
    # TODO: lọc radio, lọc khung Hà Nội, bỏ trạm ít mẫu, bỏ trùng
    raise NotImplementedError


def load_towers(path=config.TOWERS_FILE) -> pd.DataFrame:
    """Load the processed tower table (used by training and by the backend)."""
    return pd.read_csv(path)


def main() -> None:
    # TODO: load_opencellid -> filter_hanoi -> lưu config.TOWERS_FILE, in số trạm 4G và 5G
    raise NotImplementedError


if __name__ == "__main__":
    main()
