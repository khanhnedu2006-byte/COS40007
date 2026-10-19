"""All models by name, so evaluation code can loop over them."""
from speedmap.models.baselines import KNNBaseline, RandomForestBaseline
from speedmap.models.hybrid import HybridModel, PhysicsOnly, XGBoostOnly

MODELS = {
    "knn": KNNBaseline,
    "random_forest": RandomForestBaseline,
    "hybrid": HybridModel,
    "physics_only": PhysicsOnly,
    "xgboost_only": XGBoostOnly,
}

BASELINES = ["knn", "random_forest"]
MAIN_MODEL = "hybrid"
ABLATIONS = ["physics_only", "xgboost_only"]
