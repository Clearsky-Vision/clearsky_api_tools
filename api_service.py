"""
Contains Service implementing the capabilities of the ClearSky Vision API
"""

from typing import Optional, Union
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

    def _extract_filename(self, response) -> Optional[str]:
        """
        Helper method to extract filename from the response headers.
        """
        content_disposition = response.headers.get("content-disposition")
        if content_disposition:
            _, params = cgi.parse_header(content_disposition)
            return params.get("filename")
        return None

    def get_api_key_info(self) -> models.ApiKeyInfoQueryResponseDto:
        """
        Get API Key Information.
        """
        url = f"{self.BASE_URL}/api/apikey/info"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.ApiKeyInfoQueryResponseDto(**response.json())

    def search_available_imagery(self, query: models.SearchAvailableImageryQueryDto) -> models.SearchAvailableImageryQueryResponseDto:
        """
        Search Available Imagery.
        """
        url = f"{self.BASE_URL}/api/satelliteimages/search/available"
        response = requests.post(url, headers=self.headers, json=query.dict())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.SearchAvailableImageryQueryResponseDto(**response.json())

    def retrieve_estimate_for_composite_of_satellite_imagery(self, query: models.ProcessCompositeEstimateQueryDto) -> models.ProcessCompositeEstimateQueryResponseDto:
        """
        Get Estimate for Processing Composite Satellite Imagery.
        """
        url = f"{self.BASE_URL}/api/satelliteimages/process/composite/estimate"
        response = requests.post(url, headers=self.headers, json=query.dict())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.ProcessCompositeEstimateQueryResponseDto(**response.json())

    def retrieve_composite_of_satellite_imagery(
        self, directory_to_save_file: str, command: models.ProcessCompositeCommandDto
    ) -> Union[str, models.ProcessCompositeErrorResponseDto]:
        """
        Process Composite Satellite Imagery.

        If requests succeeds, it returns the path to the saved file.
        If it fails, the error response is returned
        """

        if not directory_to_save_file.endswith("/"):
            directory_to_save_file = directory_to_save_file + "/"

        os.makedirs(directory_to_save_file, exist_ok=True)

        url = f"{self.BASE_URL}/api/satelliteimages/process/composite"
        response = requests.post(url, headers=self.headers, json=command.dict(), stream=True)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        if response.status_code != 200:
            return models.ProcessCompositeErrorResponseDto(**response.json())

        filename = self._extract_filename(response)
        if not filename:
            filename = "output.tif"

        file_path = directory_to_save_file + filename

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path

    def get_tasking_models(self) -> models.TaskingModelsQueryResponseDto:
        """
        Get Models Available for Tasking.
        """
        url = f"{self.BASE_URL}/api/tasking/models"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingModelsQueryResponseDto(**response.json())

    def get_tasking_orders(self, recurring_only: bool) -> models.TaskingOrdersQueryResponseDto:
        """
        Get Tasking Orders.

        recurring_only: only retrieve recurring taskorders
        """
        url = f"{self.BASE_URL}/api/tasking/orders?recurringOnly={recurring_only}"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingOrdersQueryResponseDto(**response.json())

    def search_orderable_tiles(self, query: models.TaskingTileSearchQueryDto) -> models.TaskingTileSearchQueryResponseDto:
        """
        Search tiles available for Tasking Orders.
        """
        url = f"{self.BASE_URL}/api/tasking/search/tiles"
        response = requests.post(url, headers=self.headers, json=query.dict())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingTileSearchQueryResponseDto(**response.json())

    def cancel_recurring_order(self, taskorder_guid: str) -> bool:
        """
        Cancel Recurring Tasking Order.

        taskorder_guid: Guid identifying the Tasking Order
        """
        url = f"{self.BASE_URL}/api/tasking/orders/cancel?taskOrderGuid={taskorder_guid}"
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return response.status_code != 200
