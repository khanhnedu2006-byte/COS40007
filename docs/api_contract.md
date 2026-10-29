# API Contract

Produced by Person 3 (backend), using the bundle saved by Person 2 (notebook 06).

## GET /api/health
`{"status": "ok", "model_loaded": true}`

## GET /api/towers
```json
[{"tower_id": 1, "latitude": 21.0285, "longitude": 105.8542}, ...]
```

## GET /api/predict?lat=21.0285&lon=105.8542
```json
{
  "latitude": 21.0285, "longitude": 105.8542,
  "download_mbps": 133.0, "download_low": 95.0, "download_high": 170.0,
  "upload_mbps": 31.0, "latency_ms": 18.0,
  "quality_level": "Good",
  "theory_mbps": 223.0, "local_effect_mbps": -90.0,
  "nearest_towers": [
    {"tower_id": 1, "latitude": 21.03, "longitude": 105.85, "distance_m": 400}
  ]
}
```
Errors: `422` if the point is outside Hanoi; `503` if no model is saved yet.

## Saved model bundle (`artifacts/models/hybrid/<run>/model.joblib`)
```python
{"model": HybridModel, "conformal": ConformalInterval,
 "secondary": {"upload_mbps": XGBRegressor, "latency_ms": XGBRegressor},
 "latest_quarter_index": int}
```
