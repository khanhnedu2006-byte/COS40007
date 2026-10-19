"""Spatial block cross-validation.   Owner: Person 2

GroupKFold with groups = block_id, so neighbouring tiles never appear in both train and test.
Score only test tiles with tests >= config.MIN_TESTS_FOR_EVAL.
"""
import numpy as np
import pandas as pd

from speedmap import config


def spatial_folds(df: pd.DataFrame, n_folds: int = config.CV_FOLDS):
    """Yield (train_idx, test_idx) arrays using sklearn GroupKFold on config.GROUP_COLUMN."""
    # TODO
    raise NotImplementedError


def split_calibration(train_idx: np.ndarray, groups: np.ndarray, share: float = config.CALIBRATION_SHARE, seed: int = 0):
    """Move a share of the training BLOCKS into a calibration set for the conformal range."""
    # TODO
    raise NotImplementedError


def cross_validate(df: pd.DataFrame, model_names: list, n_folds: int = config.CV_FOLDS) -> pd.DataFrame:
    """Return one row per (fold, model) with mae, rmse, level_accuracy
    (+ coverage and interval_width for the hybrid model)."""
    # TODO
    raise NotImplementedError


def summarise(results: pd.DataFrame) -> pd.DataFrame:
    """Mean of each metric per model, sorted by MAE."""
    # TODO
    raise NotImplementedError
