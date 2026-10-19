"""OPTIONAL: OpenStreetMap features (building density, road density, land use).   Owner: Person 1

Only start this after the main pipeline works. Download once with the Overpass API,
compute one value per Ookla tile, save to data/interim/osm_features.csv.
Never call Overpass when the user clicks the map.
"""
import pandas as pd


def download_buildings(bbox: dict):
    """Download building footprints inside bbox (e.g. with the osmnx library)."""
    # TODO
    raise NotImplementedError


def building_density(lat, lon, buildings) -> pd.DataFrame:
    """Share of area covered by buildings within ~300 m of each point."""
    # TODO
    raise NotImplementedError
