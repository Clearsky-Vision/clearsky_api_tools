import os
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

WKT_POLYGON = (
    "POLYGON((-47.56709533790842 -16.086903433037758,-47.5372279798793 -16.08642134783266,-47.53672669195927 -16.115297266755253,-47.56659835292425 -16.11578026293058,-47.56709533790842 -16.086903433037758))"
)

data = client.search_available_imagery(
    wkt=WKT_POLYGON,
    from_utc="2025-06-01T00:00:01Z",
    until_utc=None,
)

print(data)