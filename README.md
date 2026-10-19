# Hanoi Mobile Internet Speed Prediction

COS40007 Design Project. Click any point on a map of Hanoi and get an estimated mobile internet speed (4G and 5G together), learned from Ookla speed tests and the distance to cell towers. Full background and decisions: `PROJECT_CONTEXT.md`.

## Project structure

```
Group project/
├── src/speedmap/                 Python package: ALL reusable code lives here
│   ├── config.py                 settings shared by everyone (paths, Hanoi box, 3GPP, levels, features)
│   ├── artifacts.py              save_model / load_model / list_runs   (ready to use)
│   ├── data/
│   │   ├── ookla.py              load + clean Ookla tiles                     P1
│   │   ├── towers.py             OpenCelliD -> Hanoi 4G/5G towers             P1
│   │   └── osm.py                OPTIONAL OpenStreetMap features              P1
│   ├── features/
│   │   ├── spatial.py            TowerIndex (BallTree), spatial blocks        P1
│   │   ├── tower_features.py     features for any points (shared w/ backend)  P1
│   │   └── build.py              -> hanoi_train.csv                           P1
│   ├── physics/
│   │   ├── propagation.py        3GPP path loss                               P2
│   │   └── link_budget.py        SINR, Shannon -> theoretical speed           P2
│   ├── models/
│   │   ├── base.py               common fit / predict interface
│   │   ├── baselines.py          KNN, Random Forest                           P2
│   │   ├── hybrid.py             main model: 3GPP + XGBoost; ablations        P2
│   │   ├── conformal.py          80% confidence range                         P2
│   │   └── registry.py           all models by name
│   ├── evaluation/
│   │   ├── metrics.py            MAE, RMSE, level accuracy, coverage          P2
│   │   ├── cv.py                 spatial block cross-validation               P2
│   │   └── plots.py              figures for the report                       P2
│   └── inference/
│       └── predictor.py          predict one clicked point                    P3
├── notebooks/                    where data is explored and models are TRAINED
│   ├── 01_explore_ookla.ipynb    P1
│   ├── 02_prepare_towers.ipynb   P1
│   ├── 03_build_features.ipynb   P1   -> data/processed/hanoi_train.csv
│   ├── 04_physics_check.ipynb    P2
│   ├── 05_train_baselines.ipynb  P2   -> artifacts/models/knn, random_forest
│   ├── 06_train_hybrid.ipynb     P2   -> artifacts/models/hybrid   (used by the backend)
│   ├── 07_evaluate_compare.ipynb P2   -> comparison table + figures
│   └── 08_test_predictor.ipynb   P3   loads the saved model like the backend
├── backend/main.py               FastAPI: /api/health, /api/towers, /api/predict    P3
├── frontend/                     React + Vite + react-leaflet map                   P3
├── scripts/
│   ├── fetch_ookla_hanoi.py      download Ookla tiles for Hanoi (done)
│   └── run_pipeline.py           run everything without notebooks
├── tests/                        pytest: physics, features, artifacts
├── docs/
│   ├── data_contract.md          columns of hanoi_train.csv (P1 <-> P2)
│   └── api_contract.md           JSON of /api/predict and the saved bundle (P2 <-> P3)
├── data/raw | interim | processed
├── artifacts/models | reports    saved models, metrics, figures
└── docx/                         specification and planning documents
```

Rules:
- **Notebooks call functions from `src/speedmap`; they do not define important logic themselves.** Then the backend can reuse exactly the same code.
- Files marked `TODO` / `NotImplementedError` are for the team to write.
- Names in English, comments in Vietnamese only where needed.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
pip install -e .                  # makes `import speedmap` work everywhere
```

## Work split

| Person | Owns | Notebooks | Delivers |
|---|---|---|---|
| **1. Data** | `data/`, `features/`, tests/test_features.py | 01, 02, 03 | `hanoi_train.csv` following `docs/data_contract.md` |
| **2. Models** | `physics/`, `models/`, `evaluation/`, tests/test_physics.py | 04, 05, 06, 07 | saved `hybrid` bundle + comparison table and figures |
| **3. Application** | `inference/`, `backend/`, `frontend/` | 08 | working map demo following `docs/api_contract.md` |

Person 2 and 3 can start before the data is ready:
- Person 2: physics code can be written and tested now with `tests/test_physics.py` (worked example 400 m + 800 m -> about 222.9 Mbps).
- Person 3: build the frontend against the example JSON in `docs/api_contract.md`.

## Workflow

```
01 explore  ->  02 towers  ->  03 features  ->  04 physics  ->  05 baselines  ->  06 hybrid (SAVE)  ->  07 compare
                                                                                        |
                                                                08 test predictor  ->  backend  ->  frontend
```

## Training in notebooks and saving models

```python
from speedmap.artifacts import save_model, load_model, list_runs

save_model(bundle, "hybrid", metrics={"mae": 41.2}, params=model.get_params())
# -> artifacts/models/hybrid/20261020-101500/model.joblib + metadata.json

bundle, meta = load_model("hybrid")                     # newest run
bundle, meta = load_model("hybrid", "20261020-101500")  # a specific run
list_runs("hybrid")
```

Every save creates a new timestamped folder, so earlier runs are never overwritten. The backend always loads the newest run unless a run id is given.

## Run the demo

```bash
uvicorn backend.main:app --reload          # http://localhost:8000/docs
cd frontend && npm install && npm run dev  # http://localhost:5173
```

## Tests

```bash
pytest                       # all
pytest tests/test_physics.py # one file
```
`test_artifacts.py` passes already; the others pass once the TODOs are written.
