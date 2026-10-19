"""Step 3c. Spatial block cross-validation (GroupKFold with groups = block_id).

Metrics on test tiles with tests >= config.MIN_TESTS_FOR_EVAL:
MAE, RMSE, quality level accuracy; for the hybrid model also interval coverage and width.
"""
import pandas as pd

from ml import config


def regression_metrics(y_true, y_pred) -> dict:
    """Return {"mae", "rmse", "level_accuracy"} (levels from config.quality_level)."""
    # TODO
    raise NotImplementedError


def cross_validate(data: pd.DataFrame, model_names=None, n_folds: int = config.CV_FOLDS) -> pd.DataFrame:
    """Train and test every model in each fold; return one row per (fold, model).

    Gợi ý: trong mỗi fold, tách khoảng 20% block của tập train để hiệu chỉnh conformal.
    """
    # TODO
    raise NotImplementedError


def summarise(results: pd.DataFrame) -> pd.DataFrame:
    """Average metrics per model, sorted by MAE."""
    # TODO
    raise NotImplementedError
