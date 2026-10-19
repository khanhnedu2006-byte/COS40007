"""Step 3a. 3GPP TR 38.901 Urban Macro (NLOS) model: distance to towers -> theoretical speed.

    PL(dB)  = 13.54 + 39.08*log10(d_m) + 20*log10(f_GHz) - 0.6*(h_UT - 1.5)
    Rx(dBm) = Tx power - PL
    SINR    = signal of nearest tower / (sum of other towers + thermal noise)
    noise   = -174 dBm/Hz + 10*log10(bandwidth_Hz) + noise figure
    speed   = bandwidth * min(log2(1 + SINR), MAX_SPECTRAL_EFFICIENCY)

Worked example (check your code against it): towers at 400 m and 800 m, NR settings
-> path loss ~126 dB, SINR ~6 dB, theoretical speed ~223 Mbps.
"""
import numpy as np

from ml import config


def path_loss_db(distance_m: np.ndarray, freq_ghz: float) -> np.ndarray:
    """Path loss in dB for each distance (clamp distance at config.MIN_DISTANCE_M)."""
    # TODO
    raise NotImplementedError


def noise_dbm(bandwidth_mhz: float) -> float:
    """Thermal noise power in dBm for the given bandwidth."""
    # TODO
    raise NotImplementedError


def theoretical_speed_mbps(distances_m: np.ndarray, radio: str) -> float:
    """Theoretical speed (Mbps) at one point from distances to towers of one technology ("NR" or "LTE").

    Trạm gần nhất là trạm phục vụ, các trạm còn lại là nhiễu. Không có trạm thì trả về 0.
    """
    # TODO: dùng config.PHYSICS[radio] cho tần số, băng thông, công suất phát
    raise NotImplementedError


def best_theoretical_speed(distances_by_radio: dict) -> float:
    """Return the higher of the NR and LTE theoretical speeds, e.g. {"NR": array, "LTE": array}."""
    # TODO
    raise NotImplementedError
