"""Shared settings for the whole project: paths, Hanoi area, physics assumptions, quality levels."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"

OOKLA_FILE = DATA_RAW / "ookla_hanoi_mobile.csv"
OPENCELLID_FILE = DATA_RAW / "452.csv.gz"  # file tải từ OpenCelliD cho Việt Nam
TOWERS_FILE = DATA_PROCESSED / "hanoi_towers.csv"
TRAIN_FILE = DATA_PROCESSED / "hanoi_train.csv"

# Khung bao gần đúng thành phố Hà Nội
HANOI_BBOX = {"lat_min": 20.53, "lat_max": 21.40, "lon_min": 105.28, "lon_max": 106.03}

RANDOM_SEED = 42

# Làm sạch
MAX_LATENCY_MS = 500
MIN_TESTS_FOR_EVAL = 3
MIN_TOWER_SAMPLES = 2

# Bán kính tìm trạm xung quanh một điểm
TOWER_SEARCH_RADIUS_M = 3000
NEAREST_TOWERS_IN_POPUP = 3

# Giả định cho mô hình 3GPP (giá trị điển hình, nhà mạng không công bố)
PHYSICS = {
    "NR": {"freq_ghz": 3.5, "bandwidth_mhz": 100, "tx_power_dbm": 46},
    "LTE": {"freq_ghz": 1.8, "bandwidth_mhz": 20, "tx_power_dbm": 46},
}
UE_HEIGHT_M = 1.5
NOISE_FIGURE_DB = 7
MIN_DISTANCE_M = 10
# Hiệu suất phổ tối đa thực tế (256-QAM), tránh Shannon cho tốc độ phi thực tế khi SINR rất cao
MAX_SPECTRAL_EFFICIENCY = 7.4

# Đánh giá
SPATIAL_BLOCK_KM = 2.0
CV_FOLDS = 5
CONFIDENCE_LEVEL = 0.80

# Mức chất lượng theo download (Mbps), xem mục 5.1 của spec
QUALITY_LEVELS = [(15, "Poor"), (100, "Fair"), (200, "Good"), (float("inf"), "Excellent")]

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
