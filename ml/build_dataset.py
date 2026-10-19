"""Build the 5G training dataset from the Raca et al. (2020) Irish 5G production traces.

Usage:
    python ml/build_dataset.py --raw data/raw/5G-production-dataset --out data/processed/5g_train.csv
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Ô lưới khoảng 250 m ở vĩ độ Cork (~52°N)
LAT_STEP = 0.00225
LON_STEP = 0.0036

MODE_MAP = {"5G": "5G", "LTE": "LTE", "HSPA+": "3G", "HSUPA": "3G", "HSDPA": "3G", "UMTS": "3G"}

# Ngưỡng download theo bảng mức trong spec (Mbps)
TIER_BINS = [-np.inf, 15, 100, 200, np.inf]
TIER_LABELS = ["Poor", "Fair", "Good", "Excellent"]


def load_traces(raw_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(raw_dir.rglob("*.csv")):
        if "__MACOSX" in path.parts:
            continue
        rel = path.relative_to(raw_dir).parts
        df = pd.read_csv(path, na_values=["-"], low_memory=False)
        df["app"] = rel[0]
        df["mobility"] = rel[1].lower()
        df["trace_id"] = path.stem
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No CSV traces found under {raw_dir}")
    return pd.concat(frames, ignore_index=True)


def build(raw: pd.DataFrame) -> pd.DataFrame:
    # Chỉ phiên tải file mới phản ánh đúng năng lực download của mạng
    df = raw[(raw["app"] == "Download") & (raw["State"] == "D")].copy()
    df = df[df["NetworkMode"].isin(MODE_MAP)]
    df = df.dropna(subset=["Latitude", "Longitude", "DL_bitrate"])

    df["timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y.%m.%d_%H.%M.%S")
    df = df.sort_values(["trace_id", "timestamp"])

    out = pd.DataFrame({
        "timestamp": df["timestamp"],
        "trace_id": df["trace_id"],
        "mobility": df["mobility"],
        "latitude": df["Latitude"].round(6),
        "longitude": df["Longitude"].round(6),
        "speed_kmh": df["Speed"],
        "hour": df["timestamp"].dt.hour,
        "weekday": df["timestamp"].dt.weekday,
        "network_mode": df["NetworkMode"].map(MODE_MAP),
        "cell_id": df["CellID"],
        "node_id": df["NODEHEX"],
        "rsrp": df["RSRP"],
        "rsrq": df["RSRQ"],
        "snr": df["SNR"],
        "cqi": df["CQI"],
        "rssi": df["RSSI"],
        "nr_rsrp": df["NRxRSRP"],
        "nr_rsrq": df["NRxRSRQ"],
        "dl_mbps": df["DL_bitrate"] / 1000,
        "ul_mbps": df["UL_bitrate"] / 1000,
        "ping_ms": df["PINGAVG"],
    })
    out["is_5g"] = (out["network_mode"] == "5G").astype(int)

    zone_y = np.floor(out["latitude"] / LAT_STEP).astype(int)
    zone_x = np.floor(out["longitude"] / LON_STEP).astype(int)
    out["zone_id"] = zone_y.astype(str) + "_" + zone_x.astype(str)

    # Throughput từng giây rất nhiễu, thêm bản làm mượt 5 giây làm mục tiêu thay thế
    out["dl_mbps_smooth5"] = (
        out.groupby("trace_id")["dl_mbps"]
        .transform(lambda s: s.rolling(5, min_periods=1, center=True).mean())
        .round(3)
    )
    out["quality_tier"] = pd.cut(out["dl_mbps_smooth5"], TIER_BINS, labels=TIER_LABELS, right=False)

    order = [
        "timestamp", "trace_id", "mobility", "latitude", "longitude", "zone_id",
        "speed_kmh", "hour", "weekday", "network_mode", "is_5g", "cell_id", "node_id",
        "rsrp", "rsrq", "snr", "cqi", "rssi", "nr_rsrp", "nr_rsrq",
        "dl_mbps", "dl_mbps_smooth5", "ul_mbps", "ping_ms", "quality_tier",
    ]
    return out[order].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw/5G-production-dataset"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/5g_train.csv"))
    args = parser.parse_args()

    data = build(load_traces(args.raw))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.out, index=False)
    print(f"Wrote {len(data):,} rows x {data.shape[1]} columns to {args.out}")


if __name__ == "__main__":
    main()
