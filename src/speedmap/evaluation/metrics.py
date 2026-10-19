"""Evaluation metrics.   Owner: Person 2"""
import numpy as np

from speedmap import config


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_pred) - np.asarray(y_true))))


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(np.mean((np.asarray(y_pred) - np.asarray(y_true)) ** 2)))


def level_accuracy(y_true, y_pred) -> float:
    """Share of points whose quality level (config.quality_level) is predicted correctly."""
    # TODO
    raise NotImplementedError


def coverage(y_true, low, high) -> float:
    """Share of true values inside [low, high]. Target: 0.75 to 0.85 for an 80% range."""
    # TODO
    raise NotImplementedError


def all_metrics(y_true, y_pred) -> dict:
    return {"mae": mae(y_true, y_pred), "rmse": rmse(y_true, y_pred), "level_accuracy": level_accuracy(y_true, y_pred)}
