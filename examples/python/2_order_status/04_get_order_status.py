import os
from clearsky_client import ClearSkyClient

API_KEY = os.environ["CLEARSKY_API_KEY"]
BASE_URL = os.getenv("CLEARSKY_BASE_URL", "https://api.clearsky.vision")

client = ClearSkyClient(api_key=API_KEY, base_url=BASE_URL)

ORDER_GUID = "PUT-YOUR-ORDER-GUID-HERE"

details = client.order_details([ORDER_GUID])
order = details["TaskOrders"][0]

print("Order GUID:", order["TaskOrderGuid"])
print("Order status:", order["OrderingProcessStatus"])

for key in ["Model", "From", "To", "CreatedDate", "TaskOrderAreaKm2"]:
    if key in order:
        print(f"{key}:", order[key])