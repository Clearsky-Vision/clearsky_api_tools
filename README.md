<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://clearsky.vision/wp-content/uploads/2020/09/clearsky_vision408.5x.png">
  <source media="(prefers-color-scheme: light)" srcset="https://clearsky.vision/wp-content/uploads/2020/09/clearsky_vision408.5x.png">
  <img alt="LOGO" src="https://clearsky.vision/wp-content/uploads/2020/09/cropped-clearsky_vision_logo_long402x-1.png">
</picture>

![ClearSKY Vision](https://clearsky.vision/wp-content/uploads/2024/01/Github_beforeafter.png)

**ClearSKY Vision**. The service delivers cloudless, multi-spectral Sentinel-2 (Level-2A) imagery. By harnessing a unique blend of data from multiple satellites, including Sentinel-1, Sentinel-2, Sentinel-3, and Landsat 8/9, and applying advanced deep learning techniques, we've successfully tackled the challenge of frequent cloud cover in traditional satellite images. The data product is comprised of estimations across 10 spectral bands from the [Sentinel-2 MultiSpectral Instrument (MSI)](https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument) Sensor. The cloudless imagery have many similarities to 'normal' Sentinel-2 and only deviate slightly to improve on the usability and accessibility of the data. 

## Table of Contents
* [Why ClearSKY Vision](#why-clearsky-vision)
* [Getting Started](#getting-started)
    * [Installation Instructions](#installation-instructions)
    * [API Credentials](#api-credentials)
    * [Data Specifications and Available Models](#data-specifications-and-available-models)
    * [Tile vs Composite Ordering](#tile-vs-composite-ordering)
* [Key Features](#key-features)
    * [Acquiring User Credentials](#acquiring-user-credentials)
    * [Data Availability](#data-availability)
    * [Requesting Estimated Credit Costs and Area](#requesting-estimated-credit-costs-and-area)
    * [Downloading a Satellite Image](#downloading-a-satellite-image)
    * [Visualizing Acquired Satellite Image](#visualizing-acquired-satellite-image)
* [Python Scripts And Tools](#python-scripts-and-tools)
* [Additional Resources](#additional-resources)
* [Frequently Asked Questions](#frequently-asked-questions)

## Why ClearSKY Vision
At ClearSKY Vision, we are committed to transforming the landscape of Earth observation. Our mission is to revolutionize the accessibility and usability of satellite imagery, making it more relevant, immediate, and actionable. Our goal is to empower researchers, innovators, and decision-makers with precise and reliable optical imagery, unlocking new possibilities in environmental monitoring, resource management, and global awareness.

This data source is unique due to the following features:
* Gain access to frequent cloudless multi-spectral imagery.
* Leverage the capabilities of seven satellites, while focusing operations on just one.
* No need for cloud and shadow masks as there are none.
* Easy to use time-series data without any missing values.
* An affordable source for up-to-date optical imagery.
* Compatible with existing Sentinel-2 applications.

![ClearSKY Vision](https://clearsky.vision/wp-content/uploads/2024/01/Output2.png)

## Getting Started

This repository contains a python API wrapper for the [ClearSKY Vision API](https://api.clearsky.vision/), as well as an example implementation for interacting with the API using the wrapper. Check out the wrapper [api_service.py](./api_service.py). It is assumed that a valid API key is available, if you do not have one check out [how to get a trial API key](#api-credentials). 

We also recommend checking out our documentation on [handling api errors](https://clearsky.vision/docs/api-error-codes/) and [api request limits](https://clearsky.vision/docs/api-request-limits/)

For further details or support, contact **info@clearsky.vision**.

### Installation Instructions
The project requirements are installed using [pip install -r ./requirements.txt](./requirements.txt). tqdm is an optional requirement used to visualize download progress. Python 3.8-3.9 and 3.12 have been verified to work, but versions >= 3.8 should work assuming requirements install successfully. 

### API Credentials
All API calls requires valid credentials which for testing purposes can be acquired from [eo.clearsky.vision](https://eo.clearsky.vision/?view=50.637867,7.826911,5.77,0.00). You can request credentials from eo.clearsky.vision by clicking "GET API KEY" and get some free credits. The credentials will be sent to the provided email straight away. 

![API KEY GIF](./get-trial-key.gif)

Alternatively, you can ask for testing access by writing to info@clearsky.vision and get in contact with a human.

### Data Specifications and Available Models
See our [data specification documentation](https://clearsky.vision/docs/data-specifications/) for information about the imagery. [Our available models](https://clearsky.vision/docs/available-models/) create images with the specified data specifications, some supporting more satellites than others. Each model has a number of mandatory satellites, as well as potential optional satellites that assist with keeping the images as up-to-date as possible.

### Tile vs Composite Ordering

Ordering satellite imagery data can be done either through tile ordering, or through composite ordering. See [a quick introduction to ordering](https://clearsky.vision/docs/tasking-order-introduction/) for details on how tiles and composites differ.

As a rule of thumb, if the ratio between your area of interest and tile area is larger than that of the tile price vs composite price, you might want to order the Tiles rather than composites as it will be cheaper.

Data ordered using tiles or composites will be accessible for a single download request using composite processing as of 2024-12-01, but there are plans (date TBD) to require additional steps for processing composite downloads in areas using ordered tiles. Imagine asynchronous processing with polling of composite processing status rather than just waiting for a response with the imagery data for the request.

You can refer to the example API code for 
* [searching orderable tiles](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L86)
* [retrieving price estimates for orders](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L86)
* [creating orders](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L142)

## Key Features:
1. **Check data availability** in your Area of Interest (AOI).
2. **Estimate download credit costs** for the requested data.
3. **Download cloud-free Sentinel-2 imagery**.
4. **Visualize acquired satellite imagery** for further analysis.

### Acquiring User Credentials

Request trial API credentials from **[ClearSKY Vision](https://eo.clearsky.vision)** by clicking "GET API KEY". You will receive some trial credits immediately. Alternatively, contact **info@clearsky.vision** for manual access. You can use the API key [in the example implementation](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L44)

### Data Availability

To automate satellite data acquisition, it is useful to check if the imagery for the ordered area and date is available. Images created for each order are by default stored for the current month + 1 additional month, and additional storage months be added to each order.

You can refer to the example API code for [searching available imagery](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L214) and [retrieving orders](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L157) to view the status of each order. These request do not consume any credits.

### Requesting Estimated Credit Costs and Area

You can estimate the download credit cost and area size before downloading imagery. This request is free and accepts the same parameters as a download request. By default each order allows for retrieving ordering imagery exactly once, but supports increasing the number of api requests to download imagery. You can refer to the example API code for [requesting composite image download estimates](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L185)

### Downloading a Satellite Image

The `PixelSelectionMode` parameter controls which pixels are included:
- **Intersect**: Includes all pixels that intersect the geometry (default).
- **Contained**: Includes only pixels fully within the geometry.

You can refer to the example API code for [processing composite image for download](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/example_clearsky_api.py#L253)

### Visualizing Acquired Satellite Image

The downloaded data is multi-spectral. Use a GeoTIFF-compatible tool (e.g. QGIS) to visualize it. For a true-color image, select the B4, B3, and B2 bands (Red, Green, and Blue) and update the image symbology to stretch the band values (e.g. setting min to 0 and max to 2000) using `stretch to MinMax` contrast enhancement so the colors make sense.

## Python Scripts And Tools

* [Example Code For Interacting with ClearSky API](./example_clearsky_api.py)
* [Service Class Wrapping ClearSky API](./api_service.py)
* [Tool for buffering a bounding box for intersect/contains pixel selection](./tools/utm_boundingbox_to_wgs84.py)
* [Tool for wrapping a wkt within a GeometryCollection as required by tasking orders](./tools/geometrycollection_wrapper.py)

## Additional Resources

* Service Homepage ([www.clearsky.vision](https://clearsky.vision/))
* Service Documentation ([www.clearsky.vision/docs](https://clearsky.vision/docs))
* API Endpoint Documentation ([api.clearsky.vision](https://api.clearsky.vision/))
* Service Uptime ([uptime.clearsky.vision](https://uptime.clearsky.vision/))
* Browse Imagery ([eo.clearsky.vision](https://eo.clearsky.vision/?view=50.637867,7.826911,5.77,0.00))

![ClearSKY Vision](https://clearsky.vision/wp-content/uploads/2024/01/github_banner.png)

## Frequently Asked Questions

* ***Is the service available in my area?***
    * The service generally allows for generating cloudless sentinel-2 imagery globally, but some areas have not yet been validated for quality. If you are interested in being one of the first to get access to a new geographical area, consider sending us a shapefile of your area of interest (info@clearsky.vision). All new areas start out with testing and free data sharing to ensure the data quality is up to par. You will get plenty of opportunities to test the imagery in your applications. 
* ***What does synthetic data mean and can I trust it?***
    * The sentinel-2 imagery data we generate is derived from deep neural networks. This is the only way to extract the necessary information available in the imagery from multiple satellite constellations. We call images derived from this process ‘synthetic’ as to not mislead users about the origin of the data. This also includes natural cloud-free data from Sentinel-2, as this data is still being processed by an artificial intelligence to ensure consistency among other things. The imagery, however, is designed to mimic normal Sentinel-2 imagery minus a few undesirable traits (clouds, shadows, missing area coverage, ...). The imagery you will find here looks and feels like Sentinel-2, and can be swapped in-place in pipelines already using the original Sentinel-2 imagery. If you would like to know more about our testing methods or accuracy, feel free to reach out at info@clearsky.vision.
* ***Is there any difference between today's data and historical data? Do you use images from the future when generating historic images?***
    * No, all data has been produced in the same way. This is to ensure consistency throughout our service. However, this also means historical data is produced without any future insights and it is only backward-looking. Our models will not interpolate between the historic date and what we know it will become in the future because they will not ingest future data even if it is available. We only extrapolate from the available historic data, from the multiple satellites we can use, what a clean image looks like.
* ***Can I access water imagery through this service?***
    * Partially. This is developed for land-based monitoring and most of open water bodies are removed after the images have been created. We do not store SAR data for open seas and it is not recommended to use any unremoved water imagery that you might find on the platform. You can find lakes consistently in our imagery, however, all water data is considerably lower quality than our land-based imagery. The recommended use of this platform (and all imagery available) is for continuous monitoring of land-based areas of interest. It has been developed with this in mind. 
* ***I'm receiving error code 500, 400, 401, or other error codes. what do they mean?***
    * [check out our error handling documentation](https://clearsky.vision/docs/api-error-codes/)
* ***How does billing work?***
    * [check out the billing documentation](https://clearsky.vision/docs/subscription-and-billing/)
* ***What do you mean by credits?***
    * [read this to understand our credit system](https://clearsky.vision/docs/understand-credit-system/)
* ***I cannot update an existing order with a new small area?***
    * Orders have some limitations, check out [our order guide](https://clearsky.vision/docs-category/order/)

## Change Log

* Updated on 2024/12/03 - showcase tasking with extended examples, update relevant documentation
* Updated on 2024/02/07

Contact us at info@clearsky.vision for more info or follow us on [LinkedIn](https://www.linkedin.com/company/clearskyvision) for updates.
