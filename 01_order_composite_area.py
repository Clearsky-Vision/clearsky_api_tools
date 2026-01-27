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

estimate = client.estimate_task_order(
    wkt=WKT_GEOMETRYCOLLECTION,
    model="Stratus2",
    satellite_constellations=["Sentinel1", "Sentinel2", "Landsat89"],
    storage_months=1,
    api_requests=1,
    image_frequency=2,
    reference_date="2024-01-01",
    from_date="2025-06-01",
    to_date="2025-06-30",
)

print(format_order_estimate(estimate))

if not ACCEPT_ESTIMATE:
    raise SystemExit(
        "Estimate not accepted. Re-run with CLEARSKY_ACCEPT_ESTIMATE=true to create the order."
    )

order = client.create_task_order(
    wkt=WKT_GEOMETRYCOLLECTION,
    model="Stratus2",
    satellite_constellations=["Sentinel1", "Sentinel2", "Landsat89"],
    storage_months=3,
    api_requests=5,
    image_frequency=2,
    reference_date="2024-01-01",
    from_date="2024-01-01",
    to_date=None,
    geometry_tile_ordering=False,
)

print("Created order:", order["TaskOrderGuid"])
print("Status:", order["OrderingProcessStatus"])