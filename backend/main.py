"""FastAPI backend for the Hanoi mobile internet speed map.   Owner: Person 3

Run from the project root (after `pip install -e .`):
    uvicorn backend.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from speedmap import config

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: khi đã có model lưu trong artifacts/models/hybrid:
    # from speedmap.inference.predictor import Predictor
    # state["predictor"] = Predictor("hybrid")
    yield
    state.clear()


app = FastAPI(title="Hanoi Mobile Internet Speed API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET"], allow_headers=["*"])


def get_predictor():
    if "predictor" not in state:
        raise HTTPException(status_code=503, detail="No model loaded yet. Train and save it in notebook 06.")
    return state["predictor"]


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": "predictor" in state}


@app.get("/api/towers")
def towers():
    return get_predictor().tower_list()


@app.get("/api/predict")
def predict(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    if not config.inside_hanoi(lat, lon):
        raise HTTPException(status_code=422, detail="Point is outside Hanoi; the model has no data there.")
    return get_predictor().predict(lat, lon)
