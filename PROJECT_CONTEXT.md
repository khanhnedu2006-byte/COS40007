# Project Context: Mobile Internet Speed Prediction for Hanoi

> **For AI assistants:** This file is the shared context for our COS40007 group project. Treat the decisions below as final unless a team member says otherwise. Do not re-suggest the rejected options in Section 12 without a new reason. When numbers here and your own knowledge disagree, trust this file and say so.
>
> Last updated: 18 October 2026.

---

## 1. Course and Project

| Item | Value |
|---|---|
| Unit | COS40007 Artificial Intelligence for Engineering, Design Project |
| Original brief | Theme 5: group zones by 5G performance and predict 5G performance (Brimbank, Melbourne) |
| What changed | The Brimbank dataset was not provided. With the supervisor's approval, the team uses its own public data for **Hanoi** and treats the topic as **mobile internet in general (4G and 5G together)** |
| Team | 3 people |
| Deliverables | Project specification, project brief, presentation, final report, working demo; a research paper is a possible extension |

## 2. Problem Statement

People in Hanoi cannot see what mobile internet speed to expect at a place before they get there. Speed-test data exists only where people have run tests. We train a model that estimates mobile internet speed at **any point in Hanoi** from its location and its **distance to cell towers**, and we show it on a web map: the user clicks a point and sees the estimated speed.

- **Unit of analysis:** one Ookla tile (about 610 m × 610 m) in one quarter.
- **Target:** average download speed of a tile (primary); upload speed and latency (secondary).
- **Output for a clicked point:** estimated download, upload, latency, an 80% confidence range for download, a quality level, and the distance to the nearest towers.

## 3. Pipeline

```
1. Ookla data for Hanoi          DONE   (30,214 rows)
2. Tower locations (OpenCelliD)  TODO   → distance from each tile to towers
3. Train models                  TODO   → 2 baselines + hybrid main model
4. Web map demo                  TODO   → Hanoi map, tower nodes, click a point → speed
```

## 4. Data

### 4.1 Ookla Open Data, mobile tiles (main dataset, labels)

- Source: Ookla Open Data on AWS (`s3://ookla-open-data`, public parquet), licence **CC BY-NC-SA 4.0** (non-commercial; must credit Ookla).
- Downloaded with `ml/fetch_ookla_hanoi.py` (reads the global parquet with DuckDB and keeps only tiles inside the Hanoi box: latitude 20.53 to 21.40, longitude 105.28 to 106.03).
- File: `data/raw/ookla_hanoi_mobile.csv`

| Column | Meaning |
|---|---|
| `quarter` | e.g. `2025-4` |
| `quadkey` | Ookla tile id (zoom 16) |
| `latitude`, `longitude` | tile centre |
| `download_mbps`, `upload_mbps` | average speed in the tile |
| `latency_ms` | average latency |
| `tests` | number of speed tests in the tile |
| `devices` | number of unique devices |

**Profile (measured on our file):**

| Fact | Value |
|---|---|
| Rows | 30,214 tile-quarters, no missing values |
| Quarters | 6: Q4 2024 to Q1 2026 |
| Unique tiles | 10,459; 1,704 tiles appear in all 6 quarters |
| Download | p5 9.7, p25 37.5, **median 70.3**, p75 128.9, p95 312.8 Mbps |
| Upload | median 24.4 Mbps |
| Latency | p25 17, **median 20**, p75 24 ms |
| Trend | median download 70.7 Mbps (Q4 2024) → 79.8 Mbps (Q1 2026) |
| Centre vs suburbs (Q1 2026) | < 5 km from Hoan Kiem: 153 Mbps; 5–10 km: 132; 10–20 km: 78; > 20 km: 67 |
| Tests per tile | 38% of records have 1 test; only 11% have ≥ 20 tests |
| Correlations with download | upload +0.60, latency −0.25, devices +0.30 |

**Known issues and how we handle them:**
- Many tiles have 1–2 tests, so they are noisy → weight each tile by `tests` in training; evaluate on tiles with ≥ 3 tests.
- Extreme values exist (latency up to 1,967 ms, download up to 1,385 Mbps), mostly single-test tiles → remove latency > 500 ms and clip extreme download in low-test tiles.
- `devices` is higher in the centre where infrastructure is also denser, so it reflects both crowding and investment; do not read it as "more users = slower".
- **The data may be out of date.** Ookla Speedtest Global Index reports Hanoi's median mobile download at **493 Mbps in August 2026** (Vietnam 206 Mbps in July 2026, 220 Mbps in August 2026; world 109 Mbps). Re-run the fetch script with newer quarters:
  `python ml/fetch_ookla_hanoi.py --quarters 2024-4 2025-1 2025-2 2025-3 2025-4 2026-1 2026-2 2026-3` (missing quarters are skipped).

### 4.2 OpenCelliD (tower locations), NOT YET DOWNLOADED

- Global crowdsourced cell tower database, licence **CC BY-SA 4.0**. Fields include `radio` (LTE, NR = 5G, ...), `mcc`, `net` (operator), `area`, `cell`, `lon`, `lat`, `range`, `samples`.
- Needs a free account token on opencellid.org; download the Vietnam file (**MCC 452**) and put it in `data/raw/`.
- Tower positions are estimated from phone reports and can be off by a few hundred metres.
- Keep LTE and NR towers inside the Hanoi box; drop towers with fewer than 2 samples.
- **First check after download:** how many LTE and NR towers fall inside Hanoi.

### 4.3 OpenStreetMap (optional features, map background)

- Building density, road density, land use around each tile, via Overpass API. Precompute per tile once; never call Overpass per click.
- Map tiles for the web demo come from OpenStreetMap (free, no API key, licence ODbL, must credit).

## 5. Features (one row per tile and quarter)

| Feature | Source |
|---|---|
| `latitude`, `longitude` | Ookla |
| distance to nearest tower (any) | OpenCelliD |
| number of towers within 500 m and 1 km | OpenCelliD |
| share of 5G (NR) towers nearby | OpenCelliD |
| building density, road density, land use (optional) | OSM |
| `devices` | Ookla |
| `quarter` | Ookla |
| theoretical speed from the 3GPP model | computed (Section 6.2) |

Distances use the haversine formula (for example scikit-learn `BallTree` with `metric="haversine"`). **The exact same feature code must be used for training and for map clicks.**

## 6. Models

### 6.1 Two baseline models (for comparison)

| Model | What it does | Why it is a baseline |
|---|---|---|
| **Baseline 1: K-Nearest Neighbours** | Average speed of the nearest measured tiles; location only | The simplest spatial rule: nearby places have similar speed |
| **Baseline 2: Random Forest** | Standard ML with the **same features** as the main model | Shows what ordinary ML achieves without physics, so any gain of the main model comes from adding physics |

### 6.2 Main model: hybrid 3GPP physics model + XGBoost

**Idea:** a physics formula estimates the speed a tile *should* get; XGBoost learns how much reality differs.

```
Step 1  3GPP model:  distances to towers → path loss → SINR → theoretical speed (Shannon)
Step 2  XGBoost:     learns  correction = real Ookla speed − theoretical speed
Result  predicted speed = theoretical speed + XGBoost correction
Step 3  Conformal prediction (MAPIE) → 80% confidence range
```

**Step 1 details**
- Path loss, 3GPP TR 38.901 Urban Macro, non-line-of-sight:
  `PL(dB) = 13.54 + 39.08·log10(d) + 20·log10(f_GHz) − 0.6·(h_UT − 1.5)`, with d in metres and h_UT ≈ 1.5 m.
- Received power = transmit power − path loss. Serving tower = nearest tower; all other nearby towers count as interference, plus thermal noise (−174 dBm/Hz + 10·log10(bandwidth) + noise figure ≈ 7 dB).
- Theoretical speed = bandwidth × log2(1 + SINR).
- Assumed settings (not public, so typical values are used; XGBoost corrects the error):
  - 5G (NR): 3.5 GHz, 100 MHz, about 46 dBm transmit power
  - 4G (LTE): 1.8 GHz, 20 MHz
  - Compute both and keep the faster one for each tile.

**Worked example:** nearest tower 400 m, another tower 800 m, 5G settings → path loss ≈ 126 dB, signal ≈ −80 dBm, interference + noise ≈ −86 dBm, SINR ≈ 6 dB → theoretical ≈ 223 Mbps. If Ookla measures 130 Mbps, the correction XGBoost must learn is −93 Mbps.

**Step 2 details**
- Inputs: the features in Section 5, including the theoretical speed.
- Target: the correction. Also try a ratio target, `log(real) − log(theoretical)`, which is often more stable.
- Sample weight: `tests`.

**Why the hybrid should beat the baselines:** physics gives a reasonable value everywhere, including areas with little data and around newly added towers; XGBoost learns real-world effects (buildings, crowding, actual equipment) that the formula cannot see. Each prediction can be explained, e.g. "theoretical 223 Mbps; this dense area is about 90 Mbps lower".

### 6.3 Evaluation

- **Spatial block cross-validation:** 5 folds, 2 km blocks, so neighbouring tiles never sit in both train and test.
- Report MAE, RMSE (Mbps) for all three models; also try the 3GPP model alone and XGBoost alone as an ablation.

## 7. Quality Levels (download)

| Level | Download | Reference |
|---|---|---|
| Poor | < 15 Mbps | Netflix recommends 15 Mbps for 4K video |
| Fair | 15 to 100 Mbps | Below the ITU IMT-2020 minimum user experienced rate (100 Mbps, ITU-R M.2410) and the world median (109 Mbps, Ookla, Aug 2026) |
| Good | 100 to 200 Mbps | Meets the ITU rate, below the Vietnam median |
| Excellent | ≥ 200 Mbps | At or above the Vietnam median (206 to 220 Mbps, Ookla, Jul–Aug 2026) |

Q1 2026 Hanoi tiles: Poor 9%, Fair 50%, Good 23%, Excellent 18%. If newer data puts most tiles in Excellent, also check levels against Hanoi quartiles.

## 8. Success Targets (from the specification)

| Measure | Target |
|---|---|
| Download MAE | Main model at least **10% lower** than the better baseline |
| Quality level accuracy | ≥ **60%** of test tiles in the correct level |
| 80% confidence range | Real value inside the range **75% to 85%** of the time |
| Response time | < **1 second** per map click |

These targets were set by the team, not by the unit; adjust after the first training run if needed and report honestly.

## 9. System Design (web demo)

```
React + Leaflet (OpenStreetMap tiles)
   │ click (lat, lon)
   ▼
FastAPI  GET /predict?lat=&lon=
   ├─ reject points outside the Hanoi box
   ├─ compute tower features (precomputed tower table + BallTree)
   ├─ look up OSM features of the tile (precomputed)
   ├─ 3GPP theoretical speed → XGBoost correction → conformal range
   └─ return JSON
   ▼
Popup: "Estimate 133 Mbps (95–170) · Good · Theoretical 223, local effect −90 · nearest tower 400 m"
```

- Map shows **4G and 5G towers as nodes** (real-world data from OpenCelliD), different colours, clustered when zoomed out.
- Recommended UX: on click, draw lines to the 3 nearest towers with distances; optional heatmap of predicted speed; a toggle to show all towers.
- Credit Ookla, OpenCelliD and OpenStreetMap on the page.

## 10. Limitations (as written in the specification)

1. Results describe mobile internet speed in general (4G and 5G together), as agreed with the supervisor.
2. OpenCelliD tower positions are estimates and may be off by a few hundred metres.
3. The 3GPP model uses typical settings (tower height, power, frequency are not public); XGBoost corrects the error.
4. Predictions show the typical speed of an area in a recent quarter, not a live measurement; the data has no time of day, so traffic congestion cannot be learned.
5. Only valid inside Hanoi; suburban tiles have fewer tests, so their ranges are wider.

## 11. Repository and Files

Local folder: `D:\VSCode file\Swinburne\COS40007\Group project`

```
Group project/
├── data/
│   ├── raw/
│   │   ├── ookla_hanoi_mobile.csv          main dataset (Hanoi)
│   │   ├── 5G-production-dataset.zip       Irish dataset, NOT used for Hanoi
│   │   └── 5G-production-dataset/          extracted Irish dataset
│   └── processed/
│       └── 5g_train.csv                    built from the Irish dataset, NOT used
├── ml/
│   ├── fetch_ookla_hanoi.py                downloads Ookla tiles for Hanoi
│   └── build_dataset.py                    Irish dataset builder, NOT used
└── docx/
    ├── PROJECT_SPECIFICATION_DEFINITION_v8.docx   LATEST specification
    └── (older versions v1 to v7 and planning documents: outdated)
```

Planned structure for new code:
```
ml/   fetch_opencellid.py, features.py (shared with backend), physics_3gpp.py,
      train_baselines.py, train_hybrid.py, evaluate.py
models/   saved models, conformal calibration, metrics.json
backend/  FastAPI app (main.py, predict endpoint)
frontend/ React + Leaflet map
notebooks/ EDA and experiments
```

**Coding conventions:** variable and function names in English; comments in Vietnamese, only where needed; Python with pandas, scikit-learn, xgboost, mapie; seeds fixed for reproducibility.

## 12. Decisions Log (do not re-open without a new reason)

| Rejected or dropped | Why |
|---|---|
| Brimbank dataset from the original brief | Not provided to the team |
| `5g_network_data.csv` (Kaggle style) | Synthetic: all correlations ≈ 0, uniform distributions, 4G with mmWave bands, US carriers in Tokyo, no coordinates |
| Irish 5G dataset (Raca et al., 2020) | Real and good, but in Cork, Ireland; cannot predict Hanoi |
| 5G-IANA open datasets | Too small or not georeferenced for this task |
| Android app reading signal (RSRP, SINR) | Too much work; the team builds a web app. Browsers cannot read radio information |
| Live traffic congestion as a learned feature | No historical traffic aligned with Ookla data; can only be shown as context |
| Time-series forecasting, clustering-only design, LLM report layer | Dropped when the project moved to the click-to-predict design |
| Raw lat/lon trained elsewhere and applied to Hanoi | Coordinates only work where training data exists |
| UAV measurements | Future work only |

## 13. Proposed Work Split (3 people)

| Person | Owns |
|---|---|
| 1. Data | OpenCelliD download and cleaning, OSM features, feature module, newer Ookla quarters, data section of the report |
| 2. Models | 3GPP physics module, baselines, hybrid model, conformal range, spatial cross-validation, evaluation section |
| 3. Application | FastAPI `/predict`, React + Leaflet map with tower nodes and popup, demo, system design section |
| All | Project brief, presentation, introduction and conclusion |

This split is a proposal; confirm within the team.

## 14. Next Steps

1. Register on OpenCelliD, download Vietnam (MCC 452), count LTE and NR towers in Hanoi. **This decides whether the tower-based design works.**
2. Re-run the Ookla script with newer quarters (2026-2, 2026-3) if available.
3. Build the feature table `data/processed/hanoi_train.csv` with tower features and `tests` as weight.
4. Train the baselines, then the hybrid model; compare with spatial CV.
5. Build the FastAPI endpoint and the Leaflet map.
6. Before claiming novelty in a paper, review related work on physics-guided ML and radio maps.

## 15. Key Sources

- Ookla Open Data: https://github.com/teamookla/ookla-open-data
- OpenCelliD: https://opencellid.org
- 3GPP TR 38.901, *Study on channel model for frequencies from 0.5 to 100 GHz* (path loss models)
- ITU-R M.2410-0 (2017), minimum technical performance requirements for IMT-2020
- Netflix speed recommendations: https://help.netflix.com/en/node/306
- Ookla Speedtest Global Index figures for Vietnam and Hanoi, as reported by VietNamNet (July 2026) and Viet Nam News (August 2026)
