from pyproj import Transformer
from shapely.geometry import Polygon


def pad_and_transform_bbox(bbox, epsg_code: int, padding: float = 0):
    """
    Pads a UTM bounding box, converts it to EPSG:4326, and constructs a WKT polygon.

    Conversion between EPSG 4326 and UTM EPSGs has some precision loss. To counteract this,
    the PixelSelectionMode can be set to intersect or contains.

    using intersect would be advisable only if the bbox is buffered with a negative value,
    i.e. the bbox is contracted.
    using contains would be advisable only if the bbox is buffered with a positive value,
    i.e. the bbox is expanded.

    Parameters:
    bbox (tuple): A tuple of (min_x, min_y, max_x, max_y) representing the bounding box.
    epsg_code (int): The EPSG code of the bounding box's coordinate system.
    padding (float): The padding value to expand/contract the bounding box.

    Returns:
    str: WKT representation of the padded bounding box in EPSG:4326.
    """
    # Pad the bounding box
    min_x, min_y, max_x, max_y = bbox
    padded_bbox = (min_x - padding, min_y - padding, max_x + padding, max_y + padding)

    # Coordinate transformation
    transformer = Transformer.from_crs(f"epsg:{epsg_code}", "epsg:4326", always_xy=True)
    min_x, min_y = transformer.transform(padded_bbox[0], padded_bbox[1])
    max_x, max_y = transformer.transform(padded_bbox[2], padded_bbox[3])

    # Create WKT Polygon
    polygon = Polygon([(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)])
    return polygon.wkt


if __name__ == "__main__":
    in_epsg = 32633
    # (min_x, min_y, max_x, max_y)
    bbox = (460590, 6299090, 462590, 6300090)
    wkt_str_polygon = pad_and_transform_bbox(bbox, in_epsg, padding=0.1)
