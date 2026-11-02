"""Run: pytest tests/test_boundary.py   (Person 1)"""
import numpy as np

from speedmap import config
from speedmap.data import boundary


def test_city_centre_is_inside():
    assert boundary.contains(21.0285, 105.8542)[0]          # Hoàn Kiếm
    assert config.inside_hanoi(21.0285, 105.8542)


def test_neighbour_provinces_are_outside():
    assert not boundary.contains(20.8133, 105.3383)[0]      # TP Hoà Bình
    assert not boundary.contains(21.3089, 105.6049)[0]      # Vĩnh Yên
    assert not config.inside_hanoi(10.7769, 106.7009)       # TP Hồ Chí Minh


def test_buffer_keeps_points_near_the_border():
    lat, lon = np.array([20.8133]), np.array([105.3383])
    far = boundary.distance_to_border_m(lat, lon)[0]
    assert not boundary.inside_or_near(lat, lon, buffer_km=far / 1000 - 1)[0]
    assert boundary.inside_or_near(lat, lon, buffer_km=far / 1000 + 1)[0]
