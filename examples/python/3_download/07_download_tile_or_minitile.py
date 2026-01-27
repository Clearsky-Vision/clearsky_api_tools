import os
from pathlib import Path
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

DATE_UTC = "2024-05-03T00:00:00Z"

# Example GUIDs (replace with real ones from your orders
TILE_GUID = "c3528462-02fc-4301-bb37-8d226b45f149"
MINITILE_GUID = "c3528462-02fc-4301-bb37-8d226b45f149"

client.download_tile(
    out_path=Path("out/tile_2024-05-03.bin"),
    tile_guid=TILE_GUID,
    date_utc=DATE_UTC,
    model="Stratus2",
)

client.download_minitile(
    out_path=Path("out/minitile_2024-05-03.bin"),
    minitile_guid=MINITILE_GUID,
    date_utc=DATE_UTC,
    model="Stratus2",
)

print("Saved tile + minitile files")