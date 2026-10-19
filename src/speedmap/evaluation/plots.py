"""Figures for the report.   Owner: Person 2 (map figures: Person 1)

Save every figure to config.ARTIFACTS_REPORTS so it can go straight into the report.
"""


def plot_model_comparison(summary, path=None):
    """Bar chart of MAE per model (baselines, main model, ablations)."""
    # TODO
    raise NotImplementedError


def plot_predicted_vs_actual(y_true, y_pred, path=None):
    """Scatter plot with the y = x line."""
    # TODO
    raise NotImplementedError


def plot_feature_importance(model, path=None):
    """XGBoost feature importance of the hybrid model."""
    # TODO
    raise NotImplementedError


def plot_speed_map(df, column="download_mbps", path=None):
    """Hanoi tiles coloured by speed (scatter of latitude/longitude)."""
    # TODO
    raise NotImplementedError
