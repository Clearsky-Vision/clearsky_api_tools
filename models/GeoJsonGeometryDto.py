import json
from typing import List, Optional
from shapely.geometry import shape


class GeoJsonGeometryDto:
    def __init__(self, type: str, coordinates=None, geometries: Optional[List["GeoJsonGeometryDto"]] = None):
        self.type: str = type  # "Polygon", "MultiPolygon", or "GeometryCollection"
        self.coordinates = coordinates
        self.geometries: Optional[List[GeoJsonGeometryDto]] = geometries

    @staticmethod
    def from_json(json_data):
        return GeoJsonGeometryDto(
            type=json_data.get("type"),
            coordinates=json_data.get("coordinates"),
            geometries=[GeoJsonGeometryDto.from_json(geometry) for geometry in json_data.get("geometries", [])] if "geometries" in json_data else None,
        )

    def to_wkt(self):
        geojson_like = self.to_dict()

        geojson_like = {k: v for k, v in geojson_like.items() if v is not None}

        shapely_geometry = shape(geojson_like)

        return shapely_geometry.wkt

    def to_dict(self):
        return {
            "type": self.type,
            "coordinates": self.coordinates,
            "geometries": [geometry.to_dict() for geometry in self.geometries] if self.geometries else None,
        }
