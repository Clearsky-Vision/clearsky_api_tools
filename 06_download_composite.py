import os
from pathlib import Path
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

WKT_POLYGON = (
    "POLYGON((-47.56709533790842 -16.086903433037758,-47.5372279798793 -16.08642134783266,-47.53672669195927 -16.115297266755253,-47.56659835292425 -16.11578026293058,-47.56709533790842 -16.086903433037758))"
)

client.download_composite(
    out_path=Path("out/composite_2025-05-05.tif"),
    wkt=WKT_POLYGON,
    date_utc="2025-05-05T00:00:00Z",
    resolution=10,
    epsg_projection=4326,
    bandnames="all",          # or "rgb" or "B2, B3, [B8_B4]" etc.
    pixel_selection_mode="contained",
    data_type="INT16",
    utm_data_selection_mode="combined_utm",
    model="StratusOptimized",
)

print("Saved out/composite_2024-05-05.tif")