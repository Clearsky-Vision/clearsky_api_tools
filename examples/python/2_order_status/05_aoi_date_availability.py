import os
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

WKT_POLYGON = (
    "POLYGON ((9.877893206725581 56.47856668238974, 10.196496722350581 56.47856668238974, "
    "10.196496722350581 56.27782087776097, 9.877893206725581 56.27782087776097, "
    "9.877893206725581 56.47856668238974))"
)

DATE_UTC = "2024-05-03T00:00:00Z"  # or "2024-05-03"
EPSG = 32632

av = client.composite_available(
    wkt=WKT_POLYGON,
    date_utc=DATE_UTC,
    epsg_projection=EPSG,
    bandnames="all",
    model="Stratus2",
    utm_data_selection_mode="combined_utm",
)

print("Availability flags:", av)

# Optional: a simple "ready/not-ready" convenience interpretation
ready = bool(av.get("FullyAvailable") and av.get("OrdersCoverPolygon") and av.get("DataAvailableForUser"))
print("Ready for download:", ready)
