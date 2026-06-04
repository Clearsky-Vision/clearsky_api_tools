<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://clearsky.vision/images/presskit/clearsky_vision_white.png">
  <source media="(prefers-color-scheme: light)" srcset="https://clearsky.vision/images/presskit/clearsky_vision_black.png">
  <img alt="LOGO" src="https://clearsky.vision/images/presskit/clearsky_vision_white.png">
</picture>

![ClearSKY Vision Banner](https://clearsky.vision/images/other/BeforeAfterBanner.png)

**ClearSKY Vision** delivers cloudless, multi-spectral Sentinel-2 (Level-2A) imagery. By harnessing a unique blend of data from multiple satellites, including Sentinel-1, Sentinel-2, Sentinel-3, and Landsat 8/9, and applying advanced deep learning techniques, we've successfully tackled the challenge of frequent cloud cover in traditional satellite images. The data product is comprised of estimations across 10 spectral bands from the [Sentinel-2 MultiSpectral Instrument (MSI)](https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument) sensor. The cloudless imagery has many similarities to “normal” Sentinel-2 and only deviates slightly to improve usability and accessibility.

## Table of Contents
* [Why ClearSKY Vision](#why-clearsky-vision)
* [Getting Started](#getting-started)
  * [Installation Instructions](#installation-instructions)
  * [API Credentials](#api-credentials)
  * [Authentication](#authentication)
  * [Data Specifications and Available Models](#data-specifications-and-available-models)
  * [Polygon vs Tile Ordering](#tile-vs-composite-ordering)
* [Key Features](#key-features)
  * [Estimate price before ordering](#estimate-price-before-ordering)
  * [Create orders](#create-orders)
  * [Order status](#order-status)
  * [Data availability](#data-availability)
  * [Downloading data](#downloading-data)
  * [Visualizing acquired satellite imagery](#visualizing-acquired-satellite-imagery)
* [Python Client and Examples](#python-client-and-examples)
* [Additional Resources](#additional-resources)
* [Frequently Asked Questions](#frequently-asked-questions)

## Why ClearSKY Vision
At ClearSKY Vision, we are committed to transforming the landscape of Earth observation. Our mission is to revolutionize the accessibility and usability of satellite imagery, making it more relevant, immediate, and actionable. Our goal is to empower researchers, innovators, and decision-makers with precise and reliable optical imagery, unlocking new possibilities in environmental monitoring, resource management, and global awareness.

This data source is unique due to the following features:
* Gain access to frequent cloudless multi-spectral imagery.
* Leverage the capabilities of multiple satellites, while focusing operations on a single, consistent output product.
* No need for cloud and shadow masks as there are none.
* Easy-to-use time-series data without missing values.
* An affordable source for up-to-date optical imagery.
* Compatible with existing Sentinel-2 applications.

![ClearSKY Vision Timeline](https://clearsky.vision/images/other/ClearSKY_Timeline.png)

## Getting Started

This repository contains:
- A lightweight Python client: **[`clearsky_client.py`](./clearsky_client.py)**
- A set of runnable scripts under **[`examples/`](./examples/)** showing the typical end-to-end workflow:
  - estimate price → create order → check status/availability → download

We also recommend reading:
- API error codes: https://docs.clearsky.vision/api-reference/error-codes
- API request limits: https://docs.clearsky.vision/api-reference/request-limits

For further details or support, contact **info@clearsky.vision**.

### Installation Instructions

This repo’s examples use `requests`. Install dependencies either via `requirements.txt` or directly:

```bash
pip install -r requirements.txt
# or
pip install requests
```

Python 3.8+ recommended.

### API Credentials

All API calls require valid credentials. You can acquire an API key from:
- https://dashboard.clearsky.vision/ (create a user and an API key)

Alternatively, you can request access by writing to **info@clearsky.vision** and get in contact with a human.

### Authentication

Authentication is done via an API key sent in the request header:

- Header name: `X-API-KEY`
- The Python client automatically attaches this header for every request.

Recommended environment variables:

```bash
export CLEARSKY_API_KEY="YOUR_API_KEY"
export CLEARSKY_BASE_URL="https://api.clearsky.vision"   # optional (default shown)
```

### Data Specifications and Available Models

See our data specification documentation for information about the imagery:
- https://docs.clearsky.vision/product-data/data-specification

Models define how imagery is fused and which satellites are supported:
- https://docs.clearsky.vision/product-data/models-stratus-nimbus

You can also discover available models programmatically via the API (and via the corresponding example scripts).

### Polygon vs Tile Ordering

Ordering satellite imagery data can be done through **polygon ordering** (AOI-based) or **tile/minitile ordering** (GUID-based). See our ordering docs for details:
- https://docs.clearsky.vision/ordering-data/choose-order-type

In general:
- **Polygon ordering** is convenient when you want to manage small and irregular areas.
- **Tile/minitile ordering** is cost-effective when your AOI aligns well with tile coverage.
- You can also request a **price-optimized tile selection** for a WKT GeometryCollection using the tile optimization endpoint and then create a tile/minitile order from the returned GUIDs.
- Mini-tile orders have a default 50% rebate compared to composite orders, meaning that if your usage requires more than 50% of a mini-tile it is more cost effecient to order the mini-tile than doing a composite order in the area. Tiles have a base rebate of 80%, meaning that if you require more than 40% of a tile it makes sense to buy the full tile instead of minitiles.

> **Important:** Always estimate the price of an order **before** creating it, and require user acceptance of the estimated cost.

Once an area is ordered, availability and downloads follow a consistent pattern:
- You can check **order status** for all orders or a specific order.
- You can check **availability** for a specific date/AOI (even when availability depends on multiple different orders).
- You can download a **composite** for an AOI regardless of whether the underlying order is tile-based or polygon-based.

---

## Key Features

### Estimate price before ordering

Before creating an order, use the **task order estimate** endpoint to preview costs and the effective coverage/dates. The estimate should be shown to the user and accepted before order creation.

See: the ordering examples in [`examples/python/1_ordering/`](./examples/python/1_ordering/).

### Create orders

There are multiple ordering flows:
1. Create a composite-area order directly from an AOI geometry, **or**
2. Search tiles/minitiles and create a tile/minitile order, **or**
3. Use tile optimization to get a cost-effective coverage for a WKT GeometryCollection, then order those tiles/minitiles.

See: the “create order” examples in [`examples/`](./examples/).

### Order status

You can check status:
- for **all orders** (list orders), or
- for a **specific order GUID** (order details)

These are typically free metadata calls and are useful to determine whether an order is ready/up-to-date.

See: the “list orders” and “get order status” examples in [`examples/python/2_order_status`](./examples/python/2_order_status/).

You can also see this information by going to https://dashboard.clearsky.vision/

### Data availability

For a specific date and AOI, you can query availability flags. This is especially helpful when an AOI is covered by multiple different orders.

You can also search for which dates are available in a given AOI and time range.

### Downloading data

Supported download paths:
- **Composite download** for an AOI (works regardless of whether the underlying order is tile-based or polygon-based)
- **Tile** download (for tile orders)
- **Minitile** download (for minitile orders)

Downloads return GeoTIFF (or server-side upload via `UploadUrl` where supported).

See: the “download composite”, “download tile/minitile”, examples in [`examples/python/3_download`](./examples/python/3_download/).

### Visualizing acquired satellite imagery

The downloaded data is multi-spectral. Use a GeoTIFF-compatible tool (e.g., QGIS) to visualize it.

For a true-color image:
- Select the **B4, B3, B2** bands (Red, Green, Blue)
- Stretch band values (example: min 0, max 2000) using *Stretch to MinMax* contrast enhancement so colors look sensible.

---

## Python Client and Examples

- **Client**: [`clearsky_client.py`](./clearsky_client.py)
  - Implements authentication, retries, JSON “ServiceResult” error handling, and binary downloads.
- **Examples**: [`examples/`](./examples/)
  - Account info + model discovery
  - Tile search and tile optimization
  - Task order estimation (price preview) and order creation
  - Order status checks (single-call)
  - Availability checks (single-call) and available-date search
  - Composite/tile/minitile downloads

---

## Additional Resources

* Service Homepage: https://clearsky.vision/
* Service Dashboard: https://dashboard.clearsky.vision/
* Service Documentation: https://docs.clearsky.vision/
* API Endpoint Documentation: https://api.clearsky.vision/
* Service Uptime: https://uptime.clearsky.vision/

## Frequently Asked Questions

* ***Is the service available in my area?***
  * The service generally allows generating cloudless Sentinel-2 imagery globally, but some areas have not yet been validated for quality. If you are interested in being one of the first to get access to a new geographical area, consider sending us a shapefile of your area of interest (**info@clearsky.vision**). All new areas start out with testing and free data sharing to ensure the data quality is up to par.

* ***What does synthetic data mean and can I trust it?***
  * The Sentinel-2 imagery data we generate is derived from deep neural networks. This is the only way to extract the necessary information available in the imagery from multiple satellite constellations. We call images derived from this process “synthetic” to avoid misleading users about the origin of the data. This also includes natural cloud-free data from Sentinel-2, as this data is still processed by AI to ensure consistency among other things. The imagery is designed to mimic normal Sentinel-2 imagery minus a few undesirable traits (clouds, shadows, missing coverage, ...). If you’d like to know more about our testing methods or accuracy, reach out at **info@clearsky.vision**.

* ***Is there any difference between today's data and historical data? Do you use images from the future when generating historic images?***
  * No. All data has been produced in the same way to ensure consistency throughout the service. Historical data is produced without any future insights and is strictly backward-looking. Our models will not ingest future data even if it is available.

* ***I'm receiving error code 500, 400, 401, or other error codes. what do they mean?***
  * Check out our error handling documentation: https://docs.clearsky.vision/api-reference/error-codes

* ***How does billing work?***
  * Check out the billing documentation: https://docs.clearsky.vision/pricing-billing/pricing-overview

* ***What do you mean by credits?***
  * Read this to understand our credit system: https://docs.clearsky.vision/pricing-billing/credits-order-vs-processing-units/

* ***I cannot update an existing order with a new small area?***
  * Orders have some limitations. See our order guide: https://docs.clearsky.vision/ordering-data/ordering-overview

Contact us at **info@clearsky.vision** for more info or follow us on [LinkedIn](https://www.linkedin.com/company/clearskyvision) for updates.
