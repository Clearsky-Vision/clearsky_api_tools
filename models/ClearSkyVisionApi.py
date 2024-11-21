from typing import Optional
import requests
import cgi
import os

import models


class ClearSkyVisionAPI:
    """
    Service class representing the ClearSky Vision API.
    """

    BASE_URL = "https://api.clearsky.vision"

    def __init__(self, api_key: str):
        """
        Initialize the service with an API key.
        """
        self.api_key = api_key
        self.headers = {"x-api-key": self.api_key}

    def get_api_key_info(self) -> models.ApiKeyInfoResponse:
        """
        Get API Key Information.
        """
        url = f"{self.BASE_URL}/api/ApiKey/GetApiKeyInfo"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return models.ApiKeyInfoResponse(**response.json())

    def search_available_imagery(
        self, query: models.SearchQueryDto
    ) -> models.SearchAvailableImageryResponse:
        """
        Endpoint 2: Search Available Imagery.
        """
        url = f"{self.BASE_URL}/api/SatelliteImages/SearchAvailableImagery"
        response = requests.post(url, headers=self.headers, json=query.dict())
        response.raise_for_status()
        return models.SearchAvailableImageryResponse(**response.json())

    def get_estimate_process_composite(
        self, query: models.ProcessCompositeEstimateQueryDto
    ) -> models.ProcessCompositeEstimateResponse:
        """
        Endpoint 3: Get Estimate for Processing Composite Satellite Imagery.
        """
        url = f"{self.BASE_URL}/api/SatelliteImages/GetEstimateProcessCompositeSatelliteImagery"
        response = requests.post(url, headers=self.headers, json=query.dict())
        response.raise_for_status()
        return models.ProcessCompositeEstimateResponse(**response.json())

    def process_composite_satellite_imagery(
        self, directory_to_save_file: str, command: models.ProcessCompositeCommandDto
    ) -> str:
        """
        Process Composite Satellite Imagery.
        Downloads the imagery file and returns the path to the saved file.
        """

        if not directory_to_save_file.endswith("/"):
            directory_to_save_file = directory_to_save_file + "/"

        os.makedirs(directory_to_save_file, exist_ok=True)

        url = f"{self.BASE_URL}/api/SatelliteImages/ProcessCompositeSatelliteImagery"
        response = requests.post(
            url, headers=self.headers, json=command.dict(), stream=True
        )
        response.raise_for_status()

        filename = self._extract_filename(response)
        if not filename:
            filename = "output.tif"

        file_path = directory_to_save_file + filename

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path

    def _extract_filename(self, response) -> Optional[str]:
        """
        Helper method to extract filename from the response headers.
        """
        content_disposition = response.headers.get("content-disposition")
        if content_disposition:
            _, params = cgi.parse_header(content_disposition)
            return params.get("filename")
        return None
