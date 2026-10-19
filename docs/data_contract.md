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
| dist_nearest_tower_m | float | metres; = search radius (3000) if no tower nearby |
| dist_nearest_nr_m | float | metres to nearest 5G tower; = 3000 if none |
| towers_500m, towers_1km | int | number of towers (4G + 5G) within the radius |
| nr_share_1km | float | share of 5G towers within 1 km (0 to 1) |
| theory_mbps | float | 3GPP theoretical speed |
| sample_weight | float | training weight, e.g. sqrt(tests) |
| block_id | int | 2 km block, used as CV groups |
| quality_level | str | Poor / Fair / Good / Excellent from download_mbps |

Model input = `config.FEATURE_COLUMNS`.
