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

data = client.search_available_imagery(
    wkt=WKT_POLYGON,
    from_utc="2024-05-01T00:00:01Z",
    until_utc=None,
)

print(data)