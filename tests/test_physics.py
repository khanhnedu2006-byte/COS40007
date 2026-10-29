"""Run: pytest tests/test_physics.py   (Person 2)"""
import numpy as np
import pytest

from speedmap.physics.propagation import path_loss_db
from speedmap.physics.link_budget import theoretical_speed_mbps


def test_path_loss_worked_example():
    assert path_loss_db(np.array([400.0]), 3.5)[0] == pytest.approx(126.1, abs=0.2)


def test_theoretical_speed_worked_example():
    assert theoretical_speed_mbps(np.array([400.0, 800.0])) == pytest.approx(222.9, abs=1.0)


def test_no_tower_gives_zero():
    assert theoretical_speed_mbps(np.array([])) == 0.0


def test_speed_is_capped():
    # Rất gần trạm: bị giới hạn bởi MAX_SPECTRAL_EFFICIENCY (100 MHz * 7.4)
    assert theoretical_speed_mbps(np.array([20.0])) == pytest.approx(740.0)

