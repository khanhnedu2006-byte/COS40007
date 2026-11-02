# Data Contract: `data/processed/hanoi_train.csv`

Produced by Person 1 (notebook 03), consumed by Person 2 (notebooks 04 to 07).
Change this file and `src/speedmap/config.py` together, and tell the team.

One row = one Ookla tile (about 610 m) in one quarter.

| Column | Type | Description |
|---|---|---|
| quarter | str | e.g. `2025-4` |
| quarter_index | int | increasing time index (year*4 + quarter - 1) |
| quadkey | str | Ookla tile id; keep as string |
| latitude, longitude | float | tile centre |
| download_mbps | float | **target** |
| upload_mbps, latency_ms | float | secondary targets |
| tests, devices | int | number of tests / devices in the tile |
| dist_nearest_tower_m | float | metres to the nearest mobile tower, not capped |
| towers_500m, towers_1km | int | number of towers within the radius |
| theory_mbps | float | 3GPP theoretical speed; empty until the physics module (T-06) is finished, then rebuild the table |
| sample_weight | float | training weight, e.g. sqrt(tests) |
| block_id | int | 2 km block, used as CV groups |
| quality_level | str | Poor / Fair / Good / Excellent from download_mbps |

Model input = `config.FEATURE_COLUMNS`.

Rebuild everything from the raw files: `python scripts/run_pipeline.py --step towers` then `--step features`.

Only tiles **inside the Hanoi administrative boundary** are kept (`data/reference/hanoi_boundary.geojson`, geoBoundaries, CC BY 4.0).

# `data/processed/hanoi_tiles.csv` (one row per tile)

Speeds pooled over the latest `config.POOL_QUARTERS` (4) quarters, weighted by the number of tests.
Less noisy than one tile in one quarter; recommended for training and for the map.

| Column | Type | Description |
|---|---|---|
| quadkey, latitude, longitude | str, float | tile id and centre |
| first_quarter, last_quarter, quarters | str, str, int | quarters that contributed data |
| download_mbps, upload_mbps | float | pooled speed: exp of the test-weighted mean of log(1 + speed), minus 1 |
| latency_ms | float | test-weighted mean latency |
| tests, devices | int | totals over the pooled quarters |
| reliability | str | `low` (< 3 tests), `medium` (3–9), `high` (>= 10) |
| dist_nearest_tower_m, towers_500m, towers_1km, theory_mbps | | same as above |
| sample_weight, block_id, quality_level | | same as above |

# `data/interim/hanoi_towers.csv`

OpenCelliD mobile cells (LTE/NR) inside Hanoi or within `config.TOWER_BUFFER_KM` (5 km) of the border, merged into towers (~100 m).
Columns: tower_id, latitude, longitude, cells, operators, samples, inside_hanoi, source (`opencellid` or `osm`).
OSM masts (`tower:type=communication`) are added only when more than 200 m from an OpenCelliD tower.
Positions are **estimated from phone measurements** (they cluster along main roads), not official site locations.

# Current version (2 Nov 2026)
Rebuild: `python scripts/run_pipeline.py --step towers` then `--step features`.
- hanoi_train.csv: 24,679 rows, 6,250 tiles inside Hanoi, quarters 2024-4 to 2026-3
- hanoi_tiles.csv: 5,212 tiles pooled over 2025-4 to 2026-3; reliability low 1,874 / medium 1,710 / high 1,628
- hanoi_towers.csv: 2,398 towers (2,315 OpenCelliD + 83 OpenStreetMap telecom masts; 2,153 inside Hanoi). Column `source` tells them apart.
