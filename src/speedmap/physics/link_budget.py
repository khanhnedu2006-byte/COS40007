"""Received power, SINR and Shannon capacity -> theoretical speed.   Owner: Person 2

    Rx(dBm)  = tx_power - path loss
    noise    = -174 dBm/Hz + 10*log10(bandwidth_Hz) + NOISE_FIGURE_DB
    SINR     = nearest tower power / (other towers' power + noise)     (add in mW, not dBm)
    speed    = bandwidth_MHz * min(log2(1 + SINR), MAX_SPECTRAL_EFFICIENCY)

Check: towers at 400 m and 800 m -> about 222.9 Mbps (see tests/test_physics.py).
"""
import numpy as np

from speedmap import config


def dbm_to_mw(dbm):
    return 10 ** (np.asarray(dbm, dtype=float) / 10)


def noise_dbm(bandwidth_mhz: float) -> float:
    # TODO
    raise NotImplementedError


def theoretical_speed_mbps(distances_m: np.ndarray) -> float:
    """Theoretical speed at one point from the distances to nearby towers; 0 if no tower."""
    # TODO: dùng config.TOWER_PHYSICS
    raise NotImplementedError
