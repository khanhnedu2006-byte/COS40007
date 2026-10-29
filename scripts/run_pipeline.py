"""Run the whole pipeline without notebooks (once every module is implemented).

Usage (from the project root):
    python scripts/run_pipeline.py --step all
    python scripts/run_pipeline.py --step towers
Steps: towers, features, baselines, hybrid, all
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from speedmap import config  # noqa: E402


def run_towers():
    from speedmap.data import towers

    hanoi = towers.filter_hanoi(towers.load_opencellid())
    config.TOWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    hanoi.to_csv(config.TOWERS_FILE, index=False)
    print(f"{len(hanoi):,} towers -> {config.TOWERS_FILE}")


def run_features():
    from speedmap.data import ookla, towers
    from speedmap.features.build import build_training_table

    clean = ookla.clean(ookla.load_raw())
    config.OOKLA_CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(config.OOKLA_CLEAN_FILE, index=False)
    train = build_training_table(clean, towers.load_towers())
    config.TRAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(config.TRAIN_FILE, index=False)
    print(f"{len(train):,} rows -> {config.TRAIN_FILE}")


def run_baselines():
    # TODO: giống notebook 05
    raise NotImplementedError


def run_hybrid():
    # TODO: giống notebook 06
    raise NotImplementedError


STEPS = {"towers": run_towers, "features": run_features, "baselines": run_baselines, "hybrid": run_hybrid}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", default="all", choices=[*STEPS, "all"])
    args = parser.parse_args()
    for name, step in STEPS.items():
        if args.step in (name, "all"):
            print(f"== {name}")
            step()


if __name__ == "__main__":
    main()
