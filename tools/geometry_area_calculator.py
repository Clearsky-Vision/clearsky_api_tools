from shapely import wkt
from pyproj import CRS, Transformer
from shapely.ops import transform


def calculate_area_ratio(wkt1: str, wkt2: str, crs_from=4326, aea_params=None):
    """
    Calculate the area ratio of two geometries using the Albers Equal Area projection.

    Parameters:
        wkt1 (str): WKT of the first geometry.
        wkt2 (str): WKT of the second geometry.
        crs_from (str): Original CRS of the WKTs (default is EPSG:4326 for WGS84).
        aea_params (dict): Parameters for the AEA projection.
                           Example: {'lon_0': 0, 'lat_0': 0}
                           Defaults to Albers Equal Area projection with global extents.

    Returns:
        float: The area ratio of the two geometries.
    """
    geom1 = wkt.loads(wkt1)
    geom2 = wkt.loads(wkt2)

    if aea_params is None:
        aea_params = {
            "proj": "aea",
            "lat_1": 20,  # First standard parallel
            "lat_2": 50,  # Second standard parallel
            "lat_0": 0,  # Latitude of origin
            "lon_0": 0,  # Central meridian
        }
    aea_crs = CRS.from_user_input(aea_params)

    transformer = Transformer.from_crs(crs_from, aea_crs, always_xy=True)
    project = lambda x, y: transformer.transform(x, y)

    geom1_projected = transform(project, geom1)  # type: ignore
    geom2_projected = transform(project, geom2)  # type: ignore

    area1 = geom1_projected.area
    area2 = geom2_projected.area

    if area2 == 0:
        raise ValueError("The area of the second geometry is zero, cannot compute ratio.")

    return area1 / area2
