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
OSM_TOWERS_RAW_FILE = DATA_RAW / "osm_comm_towers.csv"
OOKLA_CLEAN_FILE = DATA_INTERIM / "ookla_clean.csv"
TOWERS_FILE = DATA_INTERIM / "hanoi_towers.csv"
TRAIN_FILE = DATA_PROCESSED / "hanoi_train.csv"
TILES_FILE = DATA_PROCESSED / "hanoi_tiles.csv"
HANOI_BOUNDARY_FILE = ROOT / "data" / "reference" / "hanoi_boundary.geojson"

# Khu vực Hà Nội: khung bao để lọc nhanh, ranh giới thật nằm trong HANOI_BOUNDARY_FILE
HANOI_BBOX = {"lat_min": 20.54, "lat_max": 21.41, "lon_min": 105.35, "lon_max": 106.08}
HANOI_CENTER = (21.0285, 105.8542)

RANDOM_SEED = 42

# Làm sạch dữ liệu
MAX_LATENCY_MS = 500
MIN_TESTS_FOR_EVAL = 3
MIN_TOWER_SAMPLES = 2
TOWER_RADIOS = ("LTE", "NR")  # cell di động hiện đại, gộp chung thành "trạm"; không phân biệt công nghệ
TOWER_MERGE_DECIMALS = 3
TOWER_BUFFER_KM = 5
OSM_MIN_GAP_M = 200  # chỉ thêm cột OSM cách trạm OpenCelliD gần nhất trên 200 m (tránh trùng)  # giữ cả trạm ngoài ranh giới nhưng cách biên dưới 5 km

# Bảng mỗi ô một dòng (hanoi_tiles.csv)
POOL_QUARTERS = 4  # gộp các quý gần nhất để giảm nhiễu
RELIABILITY_LEVELS = [(3, "low"), (10, "medium"), (float("inf"), "high")]  # theo tổng số test của ô  # làm tròn toạ độ (~100 m) để gộp các cell thành một trạm

# Đặc trưng trạm
TOWER_SEARCH_RADIUS_M = 3000
NEAREST_TOWERS_IN_POPUP = 3

# Giả định cho mô hình 3GPP (nhà mạng không công bố, dùng giá trị điển hình)
# Một cấu hình chung cho mọi trạm (giá trị điển hình của trạm hiện đại)
TOWER_PHYSICS = {"freq_ghz": 3.5, "bandwidth_mhz": 100, "tx_power_dbm": 46}
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
    "towers_500m",
    "towers_1km",
    "theory_mbps",
    "quarter_index",
]


def quality_level(download_mbps: float) -> str:
    for upper, name in QUALITY_LEVELS:
        if download_mbps < upper:
            return name
    return QUALITY_LEVELS[-1][1]


def inside_hanoi(lat: float, lon: float) -> bool:
    """True if the point is inside the Hanoi administrative boundary."""
    from speedmap.data.boundary import contains

    return bool(contains(lat, lon)[0])
