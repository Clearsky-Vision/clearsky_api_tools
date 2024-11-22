from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Dict, List
import os

from numpy import isin

import models
from api_service import ClearSkyVisionAPI

FUNCTION = "function"
FUNCTION_ARGS = "function_args"
REQUEST_PARAMETERS = "request_parameters"
SENTINEL1 = "Sentinel1"


def main():

    api_key = "###########              REPLACE WITH API KEY              ###########"

    api_service = ClearSkyVisionAPI(api_key)

    # Get information about API key
    apikey_info = api_service.get_api_key_info()

    assert apikey_info.Data is not None

    concurrent_requests = apikey_info.Data.MaxConcurrentConnections

    ############################## ------------- ##############################
    #                            Composite Estimate                           #
    ############################## ------------- ##############################

    # allowed geometries for process composite are polygon and multipolygon
    test_wkt = "POLYGON ((8.476348 56.176533, 8.482252 56.177059, 8.482059 56.17622, 8.481894 56.175377, 8.481702 56.174142, 8.480291 56.174038, 8.480067 56.174175, 8.478484 56.175112, 8.476948 56.176049, 8.476754 56.176284, 8.476348 56.176533))"
    wkts = [test_wkt]

    estimate_dtos: List[models.ProcessCompositeEstimateQueryDto] = []

    for wkt in wkts:
        dto = models.ProcessCompositeEstimateQueryDto(
            Wkt=wkt,
            Resolution=10,
            FileType="tif",
            EpsgProjection=32632,
            DataType="int16",
            UtmDataSelectionMode="combined_utm",
            Bandnames="all",
        )

        estimate_dtos.append(dto)

    estimate_results = process_estimates(api_service, concurrent_requests, estimate_dtos)

    if any(index for index in estimate_results if not estimate_results[index][1].Succeeded):
        raise Exception("estimate failed: ")

    ############################## ------------- ##############################
    #                    Composite Processing & Download                      #
    ############################## ------------- ##############################

    composite_dtos: List[models.ProcessCompositeCommandDto] = []
    imagery_dates = [date(2024, 11, 1)]

    for estimate_dto in estimate_dtos:
        for imagery_date in imagery_dates:
            dto = models.ProcessCompositeCommandDto(
                Wkt=estimate_dto.Wkt,  # wkt must intersect an ordered area. nodata pixels will be returned in areas outside order
                Resolution=estimate_dto.Resolution,
                FileType=estimate_dto.FileType,
                EpsgProjection=estimate_dto.EpsgProjection,
                DataType=estimate_dto.DataType,
                UtmDataSelectionMode=estimate_dto.UtmDataSelectionMode,
                Bandnames=estimate_dto.Bandnames,
                Date=imagery_date,  # date must match an ordered date in the ordered area
                PixelSelectionMode="intersect",
                # satelliteconstellations and model is used to specify the order type to retrieve imagery for
                SatelliteConstellations=[
                    models.SatelliteConstellation.Sentinel1.value,
                    models.SatelliteConstellation.Sentinel2.value,
                    models.SatelliteConstellation.Landsat89.value,
                ],
                Model=models.Model.Stratus2.value,
                UtmGridForcePixelResolutionSize=False,  # UtmGridForcePixelResolutionSize forces pixel size to be Resolution meters when reprojecting
            )
            composite_dtos.append(dto)

    process_composite_results = process_composite_images(api_service, concurrent_requests, composite_dtos)

    for index, composite_result in process_composite_results.items():

        failed = not isinstance(composite_result[1], str) and not composite_result[1].Succeeded

        if failed:
            print(f"process composite job {index} failed: " + str(composite_result[1].Error.Message))
            continue

        file_path = composite_result[1]

        if not os.path.isfile(file_path):
            raise Exception("???")

        print("check file " + file_path)

    ############################## ------------- ##############################
    #                    Composite Processing & Download                      #
    ############################## ------------- ##############################

    pass


def process_composite_images(api_service: ClearSkyVisionAPI, concurrent_requests: int, dtos: List[models.ProcessCompositeCommandDto], composite_results_directory="./files/"):
    """
    Example processing and download of composite satellite imagery using the api service,

    Retrieving satellite imagery has a cost of download credits, and assumes an order is in place for the area and period
    """

    process_composite_jobs = [
        {FUNCTION: api_service.retrieve_composite_of_satellite_imagery, FUNCTION_ARGS: (composite_results_directory, dto, False), REQUEST_PARAMETERS: dto} for dto in dtos
    ]
    process_composite_results: Dict = _process_api_requests_concurrently(concurrent_requests, process_composite_jobs)
    return process_composite_results


def process_estimates(api_service: ClearSkyVisionAPI, concurrent_requests: int, dtos: List[models.ProcessCompositeEstimateQueryDto]):
    """
    Example retrieval of estimate for area size and download credit cast for processing satellite imagery using the api service

    Retrieving estimate has no cost
    """
    estimate_jobs = [{FUNCTION: api_service.retrieve_estimate_for_composite_of_satellite_imagery, FUNCTION_ARGS: (dto,), REQUEST_PARAMETERS: dto} for dto in dtos]
    estimate_results: Dict = _process_api_requests_concurrently(concurrent_requests, estimate_jobs)
    return estimate_results


def _process_api_requests_concurrently(concurrent_requests: int, jobs: List[Dict[str, Any]]) -> Dict:
    results = {}
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:

        for index, job in enumerate(jobs):
            results.setdefault(index, job[REQUEST_PARAMETERS])

        futures = {executor.submit(job[FUNCTION], *job.get(FUNCTION_ARGS, ())): index for index, job in enumerate(jobs)}

        for future in as_completed(futures):
            job_index = futures[future]
            try:
                result = future.result()
                results[job_index] = (results[job_index], result)
            except Exception as e:
                print(f"Exception occurred in job {job_index}: {e}")
                raise

    return results


if __name__ == "__main__":
    main()
