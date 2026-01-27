import os
from pathlib import Path
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

WKT_POLYGON = (
    "POLYGON ((9.877893206725581 56.47856668238974, 10.196496722350581 56.47856668238974, "
    "10.196496722350581 56.27782087776097, 9.877893206725581 56.27782087776097, "
    "9.877893206725581 56.47856668238974))"
)

client.download_composite(
    out_path=Path("out/composite_2024-05-03.tif"),
    wkt=WKT_POLYGON,
    date_utc="2024-05-03T00:00:00Z",
    resolution=10,
    epsg_projection=32632,
    bandnames="all",          # or "rgb" or "B2, B3, [B8_B4]" etc.
    pixel_selection_mode="contained",
    data_type="INT16",
    utm_data_selection_mode="combined_utm",
    model="Stratus2",
)

print("Saved out/composite_2024-05-03.tif")