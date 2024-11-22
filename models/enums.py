from enum import Enum


class SatelliteConstellation(Enum):
    Sentinel1 = "Sentinel1"
    Sentinel2 = "Sentinel2"
    Landsat89 = "Landsat89"


class Model(Enum):
    Stratus2 = "Stratus2"
