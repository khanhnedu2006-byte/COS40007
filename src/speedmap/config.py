"""Shared settings for the whole project. Change values here, not inside other modules."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Thư mục dữ liệu
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
ARTIFACTS_MODELS = ROOT / "artifacts" / "models"
ARTIFACTS_REPORTS = ROOT / "artifacts" / "reports"

# File dữ liệu
OOKLA_RAW_FILE = DATA_RAW / "ookla_hanoi_mobile.csv"
OPENCELLID_RAW_FILE = DATA_RAW / "452.csv.gz"
OOKLA_CLEAN_FILE = DATA_INTERIM / "ookla_clean.csv"
TOWERS_FILE = DATA_INTERIM / "hanoi_towers.csv"
TRAIN_FILE = DATA_PROCESSED / "hanoi_train.csv"

# Khu vực Hà Nội (gần đúng)
HANOI_BBOX = {"lat_min": 20.53, "lat_max": 21.40, "lon_min": 105.28, "lon_max": 106.03}
HANOI_CENTER = (21.0285, 105.8542)

RANDOM_SEED = 42

# Làm sạch dữ liệu
MAX_LATENCY_MS = 500
MIN_TESTS_FOR_EVAL = 3
MIN_TOWER_SAMPLES = 2
TOWER_RADIOS = ("LTE", "NR")

# Đặc trưng trạm
TOWER_SEARCH_RADIUS_M = 3000
NEAREST_TOWERS_IN_POPUP = 3

# Giả định cho mô hình 3GPP (nhà mạng không công bố, dùng giá trị điển hình)
PHYSICS = {
    "NR": {"freq_ghz": 3.5, "bandwidth_mhz": 100, "tx_power_dbm": 46},
    "LTE": {"freq_ghz": 1.8, "bandwidth_mhz": 20, "tx_power_dbm": 46},
}
UE_HEIGHT_M = 1.5
NOISE_FIGURE_DB = 7
MIN_DISTANCE_M = 10
MAX_SPECTRAL_EFFICIENCY = 7.4  # bit/s/Hz, giới hạn thực tế của 256-QAM

# Đánh giá
SPATIAL_BLOCK_KM = 2.0
CV_FOLDS = 5
CALIBRATION_SHARE = 0.2
CONFIDENCE_LEVEL = 0.80

# Mức chất lượng theo download (Mbps), xem mục 5.1 của spec
QUALITY_LEVELS = [(15, "Poor"), (100, "Fair"), (200, "Good"), (float("inf"), "Excellent")]

# Hợp đồng dữ liệu giữa phần dữ liệu và phần model, xem docs/data_contract.md
TARGET_COLUMN = "download_mbps"
SECONDARY_TARGETS = ["upload_mbps", "latency_ms"]
WEIGHT_COLUMN = "sample_weight"
GROUP_COLUMN = "block_id"
FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "dist_nearest_tower_m",
    "dist_nearest_nr_m",
    "towers_500m",
    "towers_1km",
    "nr_share_1km",
    "theory_mbps",
    "quarter_index",
]


def quality_level(download_mbps: float) -> str:
    for upper, name in QUALITY_LEVELS:
        if download_mbps < upper:
            return name
    return QUALITY_LEVELS[-1][1]


def inside_hanoi(lat: float, lon: float) -> bool:
    b = HANOI_BBOX
    return b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]
