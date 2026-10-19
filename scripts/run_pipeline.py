"""Run the whole pipeline without notebooks (once every module is implemented).

Usage (from the project root):
    python scripts/run_pipeline.py --step all
    python scripts/run_pipeline.py --step towers
Steps: towers, features, baselines, hybrid, all
"""
import argparse


def run_towers():
    # TODO: towers.load_opencellid -> filter_hanoi -> lưu config.TOWERS_FILE
    raise NotImplementedError


def run_features():
    # TODO: ookla.clean -> build_training_table -> lưu config.TRAIN_FILE
    raise NotImplementedError


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
