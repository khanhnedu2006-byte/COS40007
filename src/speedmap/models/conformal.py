"""Split conformal prediction: 80% confidence range around any fitted model.   Owner: Person 2

    scores = |y_calib - y_pred_calib|
    q      = quantile(scores, ceil((n + 1) * level) / n)
    range  = [max(0, y_pred - q), y_pred + q]

Ý tưởng cải tiến sau: chia score theo độ khó (ví dụ theo số lượt test) để khoảng rộng hẹp khác nhau.
"""
import numpy as np

from speedmap import config


class ConformalInterval:
    def __init__(self, level: float = config.CONFIDENCE_LEVEL):
        self.level = level
        self.q = None

    def calibrate(self, y_true: np.ndarray, y_pred: np.ndarray):
        # TODO
        raise NotImplementedError

    def interval(self, y_pred: np.ndarray):
        # TODO
        raise NotImplementedError
