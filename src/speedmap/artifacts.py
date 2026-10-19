"""Save and load trained models so notebooks can train and the backend can reuse them.

Layout:
    artifacts/models/<name>/<YYYYmmdd-HHMMSS>/model.joblib
    artifacts/models/<name>/<YYYYmmdd-HHMMSS>/metadata.json
    artifacts/models/<name>/LATEST            (text file with the newest run folder name)

Example:
    path = save_model(bundle, "hybrid", metrics={"mae": 41.2}, params={...})
    bundle, meta = load_model("hybrid")              # newest run
    bundle, meta = load_model("hybrid", "20261020-101500")
"""
import json
from datetime import datetime
from pathlib import Path

import joblib

from speedmap import config


def save_model(obj, name: str, metrics: dict | None = None, params: dict | None = None,
               feature_columns: list | None = None, notes: str = "") -> Path:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = config.ARTIFACTS_MODELS / name / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(obj, run_dir / "model.joblib")
    metadata = {
        "name": name,
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "feature_columns": feature_columns or list(config.FEATURE_COLUMNS),
        "metrics": metrics or {},
        "params": params or {},
        "notes": notes,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    (config.ARTIFACTS_MODELS / name / "LATEST").write_text(run_id, encoding="utf-8")
    return run_dir


def load_model(name: str, run_id: str | None = None):
    model_dir = config.ARTIFACTS_MODELS / name
    if run_id is None:
        latest = model_dir / "LATEST"
        if not latest.exists():
            raise FileNotFoundError(f"No saved model named '{name}' in {config.ARTIFACTS_MODELS}")
        run_id = latest.read_text(encoding="utf-8").strip()
    run_dir = model_dir / run_id
    obj = joblib.load(run_dir / "model.joblib")
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    return obj, metadata


def list_runs(name: str) -> list:
    model_dir = config.ARTIFACTS_MODELS / name
    if not model_dir.exists():
        return []
    return sorted(p.name for p in model_dir.iterdir() if p.is_dir())
