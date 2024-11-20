
# ClearSky API Tools

This repository demonstrates how to utilize the Processing API from ClearSky Vision to acquire cloud-free Sentinel-2 imagery. The guide includes Python code examples that show you how to download high-quality Earth observation data easily. 

### Key Features:
1. **Check data availability** in your Area of Interest (AOI).
2. **Estimate area and credit costs** for the requested data.
3. **Download cloud-free Sentinel-2 imagery**.
4. **Visualize acquired satellite imagery** for further analysis.

Feel free to contact **info@clearsky.vision** for any questions or issues.

---

## Table of Contents

- [Importing Libraries](#importing-libraries)
- [Acquiring User Credentials](#acquiring-user-credentials)
- [Functions for 'Data Availability'](#functions-for-data-availability)
- [Requesting 'Data Availability'](#requesting-data-availability)
- [Functions for Estimating Credit Cost and Area](#functions-for-estimating-credit-cost-and-area)
- [Requesting Estimated Credit Costs and Area](#requesting-estimated-credit-costs-and-area)
- [Functions for Downloading Imagery](#functions-for-downloading-imagery)
- [Downloading a Single Satellite Image](#downloading-a-single-satellite-image)
- [Visualizing Acquired Satellite Image](#visualizing-acquired-satellite-image)

---

## Importing Libraries

Install the necessary Python libraries for running the examples:

```bash
pip install requests tqdm
```

---

## Acquiring User Credentials

Request trial API credentials from **[ClearSky Vision](https://eo.clearsky.vision)** by clicking "GET API KEY". You will receive €125 worth of credits immediately via email. Alternatively, contact **info@clearsky.vision** for manual access.

```python
class User:
    def __init__(self, api_key):
        self.api_key = api_key

credentials = User(api_key="XXXXXXXXXXXXXXXXXXXXXX")
```

---

## Functions for 'Data Availability'

To automate satellite data acquisition, it’s useful to check if the imagery for today is available. This avoids surprises, especially for large AOIs that may cross multiple tiles. The API call is free but requires an API key.

Refer to the code from **`/api_tools/example_api.py`** (lines 30-60).

```python
<example code from file>
```

---

## Requesting 'Data Availability'

The 'Data Availability' endpoint provides four key categories:
- **IntersectedActiveZones**: `True` if tiles intersecting the AOI are found.
- **FullyAvailable**: `True` if all intersecting tiles contain imagery for the requested date.
- **PolygonInDataArea**: `True` if the AOI is in a data-accessible region.
- **DataAvailableForUser**: `False` if access is restricted for the specified date/area.

Refer to **`/api_tools/example_api.py`** (lines 70-80).

```python
<example code from file>
```

---

## Requesting Estimated Credit Costs and Area

You can estimate the credit cost and area size before downloading imagery. The endpoint also provides processing time and file size. This call is free and requires the same parameters as a download request.

Refer to **`/api_tools/example_api.py`** (lines 90-100).

```python
<example code from file>
```

---

## Downloading a Single Satellite Image

The `PixelSelectionMode` parameter controls which pixels are included:
- **Intersect**: Includes all pixels that intersect the bounding box (default).
- **Contained**: Includes only pixels fully within the bounding box.

Refer to **`/api_tools/example_api.py`** (lines 110-140).

```python
<example code from file>
```

---

## Visualizing Acquired Satellite Image

The downloaded data is multi-spectral. Use a GeoTIFF-compatible tool (e.g., QGIS) to visualize it. For a true-color image, select the B4, B3, and B2 bands (Red, Green, and Blue).

---

For further details or support, contact **info@clearsky.vision**.
