"""
Contains Service implementing the capabilities of the ClearSky Vision API
"""

from datetime import datetime
import shutil
from typing import Optional, Union
import uuid
import requests
import cgi
import os

from tqdm import tqdm  # for progress bar only

import models


class ClearSkyVisionAPI:
    """
    Service class representing the ClearSky Vision API.
    """

    BASE_URL = "https://api.clearsky.vision"

    def __init__(
        self,
        api_key: str,
    ):
        """
        Initialize the service with an API key.
        """
        self.api_key = api_key
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json, application/octet-stream",
            "Content-Type": "application/json",
        }

    def _extract_filename_from_headers(
        self,
        response: requests.Response,
    ) -> Optional[str]:
        """
        Helper method to extract filename from the response headers.
        """
        content_disposition = response.headers.get("content-disposition")
        if content_disposition:
            _, params = cgi.parse_header(content_disposition)
            return params.get("filename")
        return None

    def get_api_key_info(
        self,
    ) -> models.ApiKeyInfoQueryResponseDto:
        """
        Get API Key Information.
        """
        url = f"{self.BASE_URL}/api/apikey/info"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.ApiKeyInfoQueryResponseDto.parse_obj(response.json())

    def search_available_imagery(
        self,
        query: models.SearchAvailableImageryQueryDto,
    ) -> Union[models.SearchAvailableImageryQueryResponseDto, models.ServiceResultError]:
        """
        Search Available Imagery.
        """
        url = f"{self.BASE_URL}/api/satelliteimages/search/available"
        response = requests.post(url, headers=self.headers, data=query.json())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        if response.status_code != 200:
            return models.ServiceResultError(**response.json())

        return models.SearchAvailableImageryQueryResponseDto.parse_obj(response.json())

    def retrieve_estimate_for_composite_of_satellite_imagery(
        self,
        query: models.ProcessCompositeEstimateQueryDto,
    ) -> models.ProcessCompositeEstimateQueryResponseDto:
        """
        Get Estimate for Processing Composite Satellite Imagery.
        """
        url = f"{self.BASE_URL}/api/satelliteimages/process/composite/estimate"
        response = requests.post(url, headers=self.headers, data=query.json())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.ProcessCompositeEstimateQueryResponseDto.parse_obj(response.json())

    def retrieve_composite_of_satellite_imagery(
        self,
        directory_to_save_file: str,
        command: models.ProcessCompositeCommandDto,
        show_progress=True,
    ) -> Union[str, models.ServiceResultError]:
        """
        Process Composite Satellite Imagery.

        If requests succeeds, it returns the path to the saved file.
        If it fails, the error response is returned

        see tools/utm_utm_boundingbox_to_wgs84.py for details on how to use PixelSelectionMode
        with a boundingbox as the command geometry if you require precise pixels to be returned
        """

        if not directory_to_save_file.endswith("/"):
            directory_to_save_file = directory_to_save_file + "/"

        os.makedirs(directory_to_save_file, exist_ok=True)

        url = f"{self.BASE_URL}/api/satelliteimages/process/composite"
        request_start = datetime.now()
        with requests.post(url, headers=self.headers, data=command.json(), stream=True) as response:

            if response.status_code == 401:
                raise Exception("API Key is Unauthorized")

            if response.status_code != 200:
                return models.ServiceResultError(**response.json())

            file_path = self._download_file_with_tdqm_progress(directory_to_save_file, show_progress, request_start, command.FileType, response)

            return file_path

    def _download_file_with_tdqm_progress(self, directory_to_save_file: str, show_progress: bool, request_start: datetime, file_extension: str, response: requests.Response):
        filename = self._extract_filename_from_headers(response)
        if not filename:
            filename = f"output-{uuid.uuid4()}.{file_extension}"

        file_path = directory_to_save_file + filename
        incomplete_file_path = file_path + ".incomplete"
        request_end: Optional[datetime] = None

        with tqdm(unit="B", unit_scale=True, disable=not show_progress) as progress:
            chunk_size = 2**20
            with open(incomplete_file_path, "wb") as incomplete_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        if request_end is None:
                            request_end = datetime.now()
                            print("Request complete, time elapsed: " + str((request_end - request_start).seconds) + " seconds, starting download")
                        incomplete_file.write(chunk)
                        progress.update(len(chunk))

        shutil.move(incomplete_file_path, file_path)
        return file_path

    def get_tasking_models(
        self,
    ) -> models.TaskingModelsQueryResponseDto:
        """
        Get Models Available for Tasking.
        """
        url = f"{self.BASE_URL}/api/tasking/models"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingModelsQueryResponseDto.parse_obj(response.json())

    def get_tasking_orders(
        self,
        recurring_only: bool,
    ) -> models.TaskingOrdersQueryResponseDto:
        """
        Get Tasking Orders.

        recurring_only: only retrieve recurring taskorders
        """
        url = f"{self.BASE_URL}/api/tasking/orders?recurringOnly={recurring_only}"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingOrdersQueryResponseDto.parse_obj(response.json())

    def search_orderable_tiles(
        self,
        query: models.TaskingTileSearchQueryDto,
    ) -> models.TaskingTileSearchQueryResponseDto:
        """
        Search tiles available for Tasking Orders.
        """
        url = f"{self.BASE_URL}/api/tasking/search/tiles"
        response = requests.post(url, headers=self.headers, json=query.dict())

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return models.TaskingTileSearchQueryResponseDto.parse_obj(response.json())

    def cancel_recurring_order(
        self,
        taskorder_guid: str,
    ) -> bool:
        """
        Cancel Recurring Tasking Order.

        taskorder_guid: Guid identifying the Tasking Order
        """
        url = f"{self.BASE_URL}/api/tasking/orders/cancel?taskOrderGuid={taskorder_guid}"
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 401:
            raise Exception("API Key is Unauthorized")

        return response.status_code != 200
