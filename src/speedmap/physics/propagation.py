"""3GPP TR 38.901 Urban Macro, non-line-of-sight path loss.   Owner: Person 2

    PL(dB) = 13.54 + 39.08*log10(d_m) + 20*log10(f_GHz) - 0.6*(h_UT - 1.5)
Clamp d at config.MIN_DISTANCE_M. Check: 400 m at 3.5 GHz -> about 126.1 dB.
"""
import numpy as np


def path_loss_db(distance_m: np.ndarray, freq_ghz: float) -> np.ndarray:
    # TODO
    raise NotImplementedError
