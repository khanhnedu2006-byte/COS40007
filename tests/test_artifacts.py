"""Run: pytest tests/test_artifacts.py   (works already)"""
from speedmap import artifacts, config


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ARTIFACTS_MODELS", tmp_path)
    artifacts.save_model({"weights": [1, 2, 3]}, "dummy", metrics={"mae": 1.5})
    obj, meta = artifacts.load_model("dummy")
    assert obj == {"weights": [1, 2, 3]}
    assert meta["metrics"]["mae"] == 1.5
    assert len(artifacts.list_runs("dummy")) == 1
