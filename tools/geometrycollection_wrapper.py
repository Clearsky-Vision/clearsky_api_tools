from shapely import wkt
from shapely.geometry import GeometryCollection


def wrap_in_geometrycollection(test_wkt: str) -> str:
    geometry = wkt.loads(test_wkt)
    if not isinstance(geometry, GeometryCollection):
        return GeometryCollection([geometry]).wkt
    return geometry.wkt
