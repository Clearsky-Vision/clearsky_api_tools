# Welcome ClearSKY Vision

![ClearSky Vision](https://clearsky.vision/wp-content/uploads/2024/01/github_banner.png)

> **ClearSKY Vision**. The service delivers cloudless, multi-spectral Sentienl-2 (Level-2A) imagery. By harnessing a unique blend of data from multiple satellites, including Sentinel-1, Sentinel-2, Sentinel-3, and Landsat 8/9, and applying advanced deep learning techniques, we've successfully tackled the challenge of frequent cloud cover in traditional satellite images. The data product is comprised of estimations across 10 spectral bands from the Sentinel-2 MultiSpectral Instrument (MSI) Sensor. The cloudless imagery have many similarities to 'normal' Sentinel-2 and only deviate slightly to improve on the usability and accessibility of the data.

## Table of Contents
* [Getting Started](#Getting-Started)
* [Python Scripts:](#Python-Scripts)
    * Tile API 
    * Processing API 
* [Jupyter Notebooks:](#Jupyter-Notebooks)
    * Processing API
* [Additional Resources](#Additional-Resources)
* [Frequently Asked Questions](#Frequently-Asked-Questions)

## Getting Started


### API Credentials
All API calls requires valid credentials which for testing purposes can be acquired from eo.clearsky.vision. You can request credentials from eo.clearsky.vision by clicking "GET API KEY" and get €125 worth of credits. The credentials will be sent to the provided email straightaway. 

![API KEY GIF](https://clearsky.vision/wp-content/uploads/2024/01/Github_GIF.gif)

Alternatively, you can ask for access by writing to info@clearsky.vision and get in contact with a human.

### Data Specifications 
The imagery is available as multi-spectral GeoTIFFs with the following spectral bands:

| **Band Name**      | **Band ID** |  **Resolution (m)**    |  **Wavelength (nm)**  |  **Band Order**    |
|  :----     |    :----:   |     :----:  |    :----:  |      :----:  |
| **Blue**      | B2       | 10   |    492 ± 33   |   1    |
| **Green**      | B3        | 10      |    559 ± 18   |    2   |
| **Red**      | B4       | 10   |   	664 ± 15    |    3   |
| **Red-Edge 1**      | B5        | 10      |    704 ± 8   |    4   |
| **Red-Edge 2**      | B6       | 10   |      	740 ± 7  |    5  |
| **Red-Edge 3**      | B7        | 10      |     782 ± 10   |    6   |
| **Near Infrared**       | B8       | 10   |    732 ± 53   |    7   |
| **Narrow Near Infrared**      | B8a        | 10      |   864 ± 11  |    8   |
| **Shortwave Infrared 1**     | B11       | 10   |   1613 ± 47  |    9   |
| **Shortwave Infrared 2**    | B12        | 10      |  2200 ± 92  |    10   |

The cloudless data has been corrected with Sen2Cor for bottom-of-atmosphere disturbance beforehand. Furthermore, all of our Sentinel-2 data is **harmonized to the [pre-January 25. baseline](https://sentinels.copernicus.eu/web/sentinel/-/copernicus-sentinel-2-major-products-upgrade-upcoming)**. This is to allow for more efficient time-series analysis across multiple years.

### Tile or Processing API?

* **Tile API:** A ClearSky Vision tile is always 2602 km2 (5120x5120 px) and it may contain no-data near shores or UTM zone transitions. A tile is returned as a Cloud Optimized GeoTIFF (COG), meaning it contains multiple resolutions that can be extracted one-by-one. 
* **Processing API:** You only pay for the data you need. The Processing API can cut and merge tiles into custom bounding boxes (including single and multipolygons), reproject coordinates, calculate indices ((A+B)/(A-B)), and/or downscale resolution. It's purpose it to deliver analysis-ready data in whatever format that is required by the user. 

As a rule of thumb, if your area of interest is larger than 10% of a tile (~260.2 km), you might want to utilize the Tile API as it will be cheaper in credits. Our tiles are also faster to acquire (in terms of MB/s), as there is no processing happening. 


## Python Scripts

* [Tile API Code Example](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/api_tools/example_tile_api.py)
* [Processing API Code Example](https://github.com/Clearsky-Vision/clearsky_api_tools/blob/main/api_tools/examples_processing_api.py)

## Jupyter Notebooks


* Processing API Code Example 

## Additional Resources

* Service Homepage (www.clearsky.vision)
* Swagger API Docs (www.api.clearsky.vision)
* Service Uptime (www.uptime.clearsky.vision)
* Browse Imagery (www.eo.clearsky.vision)

## Frequently Asked Questions

* ***Why is the service not available in my area?***
    * The service is time-consuming and expensive to run as a small startup. If you are interested in being one of the first to get access to a new geographical area, consider sending us a shapefile of your area of interest (info@clearsky.vision). All new areas start out with testing and free data sharing. You will get plenty of opportunities to test the imagery in your applications. 
* ***What does synthetic data mean and can I trust it?***
    * data available on eo.clearsky.vision is derived from deep neural networks because this is the only way to extract the necessary information available in the images. We call images derived from this process ‘synthetic’ to not mislead users about the origin of the data. This also includes natural cloud-free data from Sentinel-2, as this data is still being processed by an artificial intelligence to ensure consistency among other things. The imagery, however, is designed to mimic normal Sentinel-2 imagery minus a few undesirable traits. The imagery you will find here looks and feels like Sentinel-2. If you would like to know more about our testing methods or accuracy, feel free to reach out at info@clearsky.vision.
* ***Is there any difference between today's data and historical data?***
    * No, all data has been produced in the same way. This is to ensure consistency throughout our service. However, this also means historical data is produced without any future insights and it’s only backward-looking. It will not extrapolate into what we know it will become because it will not see future data even if we do have it available.
* ***Can I access water imagery through this service?***
    * No. This is developed for land-based monitoring and all open water bodies are removed after the images have been created. We do not store SAR data for open seas and it’s not recommended to use any unremoved water imagery that you mind find on the platform. You can find lakes consistently in our imagery, however, all water data is considerably lower quality than our land-based imagery. The recommended use of this platform (and all imagery available) is for continuous monitoring of land-based areas of interest. It has been developed for vegetation monitoring. 
* ***I'm receiving error code 401, what does that mean?***
    * It means unauthorized access which is due to missing or incorrect credentials. 
* ***I'm receiving error code 1002, what does that mean?***
    * It means there is no data available for the area and/or date requested. This can be due to us not supporting the area or not having produced data for that particular day. Try another day in the same area or write to info@clearsky.vision to hear about the possibilites for extending the service area. 

Contact us at info@clearsky.vision for more info or follow us on [LinkedIn](https://www.linkedin.com/company/clearskyvision) for updates.

> Updated on 2024/01/19
