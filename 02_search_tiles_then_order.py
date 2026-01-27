import os
from clearsky_client import ClearSkyClient, format_order_estimate

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")
ACCEPT_ESTIMATE = False # Set to True to accept the estimate

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

WKT_GEOMETRYCOLLECTION = (
    "GEOMETRYCOLLECTION ("
    "POLYGON ((9.563103 50.703336, 9.730644 50.703336, 9.730644 50.80759, 9.563103 50.80759, 9.563103 50.703336))"
    ")"
)

model="Stratus2"
satellite_constellations=["Sentinel1", "Sentinel2", "Landsat89"]
storage_months=1
api_requests=1
image_frequency=2
reference_date="2024-01-01"
from_date="2025-06-01"
to_date="2025-06-30"


tiles_data = client.search_tiles(wkt=WKT_GEOMETRYCOLLECTION)
tiles = tiles_data.get("Tiles", [])

tile_guids = [t["Guid"] for t in tiles[:3] if not t.get("MiniTile", False)]

estimate = client.estimate_task_order(
    tile_guids=tile_guids,
    model=model,
    satellite_constellations=satellite_constellations,
    storage_months=storage_months,
    api_requests=api_requests,
    from_date=from_date,
    to_date=to_date,
)

print(format_order_estimate(estimate))

if not ACCEPT_ESTIMATE:
    raise SystemExit("Estimate not accepted. Set CLEARSKY_ACCEPT_ESTIMATE=true to create the order.")

order = client.create_task_order(
    tile_guids=tile_guids,
    model=model,
    satellite_constellations=satellite_constellations,
    storage_months=storage_months,
    api_requests=api_requests,
    from_date=from_date,
    to_date=to_date,
)

print("Created order:", order["TaskOrderGuid"])