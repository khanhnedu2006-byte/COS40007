"""Group Task 2: training step of the GitHub Actions pipeline.

Trains a small neural network (TensorFlow) that predicts mobile download speed in Hanoi
from the location and the cell-tower features built by our data pipeline, then saves
model_results.png and metrics.txt for the workflow to upload.

Data: data/ci/hanoi_train.csv, a snapshot of data/processed/hanoi_train.csv
(rebuild with: python scripts/run_pipeline.py --step features).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # chạy trên máy chủ không có màn hình
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "ci" / "hanoi_train.csv"
FEATURES = ["latitude", "longitude", "dist_nearest_tower_m", "towers_500m", "towers_1km", "quarter_index"]
TARGET = "download_mbps"
TEST_SHARE = 0.2
MIN_TESTS_FOR_EVAL = 3
QUALITY_LEVELS = [(15, "Poor"), (100, "Fair"), (200, "Good"), (float("inf"), "Excellent")]
SEED = 42


def quality_level(mbps: float) -> str:
    return next(name for upper, name in QUALITY_LEVELS if mbps < upper)


def prepare(df: pd.DataFrame) -> np.ndarray:
    x = df[FEATURES].astype("float32").copy()
    x["dist_nearest_tower_m"] = np.log1p(x["dist_nearest_tower_m"])  # khoảng cách trải rộng, dùng log
    return x.to_numpy()


def spatial_split(df: pd.DataFrame):
    """Hold out 20% of the 2 km blocks, so test tiles are not neighbours of training tiles."""
    rng = np.random.default_rng(SEED)
    blocks = df["block_id"].unique()
    test_blocks = rng.choice(blocks, size=int(len(blocks) * TEST_SHARE), replace=False)
    is_test = df["block_id"].isin(test_blocks)
    return df[~is_test], df[is_test]


def build_model(x_train: np.ndarray) -> tf.keras.Model:
    norm = tf.keras.layers.Normalization()
    norm.adapt(x_train)
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(x_train.shape[1],)),
        norm,
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(1),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse", metrics=["mae"])
    return model


def main() -> None:
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    df = pd.read_csv(DATA_FILE)
    train, test = spatial_split(df)
    x_train, x_test = prepare(train), prepare(test)
    # Học trên log tốc độ vì phân bố download lệch phải; trọng số = sqrt(số test)
    y_train = np.log1p(train[TARGET].to_numpy("float32"))
    w_train = train["sample_weight"].to_numpy("float32")

    model = build_model(x_train)
    history = model.fit(
        x_train, y_train, sample_weight=w_train,
        validation_split=0.2, epochs=40, batch_size=256, verbose=2,
        callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)],
    )

    # Đánh giá trên các ô test có ít nhất 3 lần đo
    test = test[test["tests"] >= MIN_TESTS_FOR_EVAL]
    y_true = test[TARGET].to_numpy()
    y_pred = np.expm1(model.predict(prepare(test), verbose=0).ravel())
    baseline = np.full_like(y_true, np.median(train[TARGET]))

    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - y_true.mean()) ** 2)
    # Download lệch phải nên R2 trên log tốc độ phản ánh đúng hơn mục tiêu mà mô hình học
    lt, lp = np.log1p(y_true), np.log1p(y_pred)
    r2_log = 1 - np.sum((lt - lp) ** 2) / np.sum((lt - lt.mean()) ** 2)
    base_mae = np.mean(np.abs(y_true - baseline))
    level_acc = np.mean([quality_level(a) == quality_level(b) for a, b in zip(y_true, y_pred)])

    metrics = (
        "Hanoi mobile download speed - neural network (TensorFlow)\n"
        f"Data: {len(df):,} tile-quarter rows, {df['quadkey'].nunique():,} tiles, "
        f"quarters {df['quarter'].min()} to {df['quarter'].max()}\n"
        f"Split: spatial blocks (2 km), train {len(train):,} rows, test {len(test):,} rows with >= {MIN_TESTS_FOR_EVAL} tests\n"
        f"Features: {', '.join(FEATURES)}\n"
        f"Epochs trained: {len(history.history['loss'])}\n\n"
        f"MAE  (Mbps): {mae:.2f}\n"
        f"RMSE (Mbps): {rmse:.2f}\n"
        f"R2 (Mbps)      : {r2:.3f}\n"
        f"R2 (log speed) : {r2_log:.3f}\n"
        f"Quality level accuracy: {level_acc:.1%}\n"
        f"Baseline MAE (median of training set): {base_mae:.2f}\n"
        f"Improvement over baseline: {(1 - mae / base_mae):.1%}\n"
    )
    (ROOT / "metrics.txt").write_text(metrics, encoding="utf-8")
    print(metrics)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(history.history["loss"], label="train")
    axes[0].plot(history.history["val_loss"], label="validation")
    axes[0].set_title("Training loss (MSE on log speed)")
    axes[0].set_xlabel("epoch")
    axes[0].legend()

    axes[1].scatter(y_true, y_pred, s=5, alpha=0.4)
    lims = [1, max(y_true.max(), y_pred.max())]
    axes[1].plot(lims, lims, "r--", label="perfect prediction")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("actual download (Mbps)")
    axes[1].set_ylabel("predicted download (Mbps)")
    axes[1].set_title(f"Test tiles: MAE {mae:.1f} Mbps, R2 (log) {r2_log:.2f}")
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(ROOT / "model_results.png", dpi=120)
    print("Saved model_results.png and metrics.txt")


if __name__ == "__main__":
    main()
