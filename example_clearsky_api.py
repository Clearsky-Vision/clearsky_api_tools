from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
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

    ############################## ------------- ##############################
    #                                  Setup                                  #
    ############################## ------------- ##############################

    required_bands = "all"
    # required_bands = "B4,B3,B2,B5,B6,B7,B8,B8A,B11,B12"
    test_wkt = "POLYGON ((8.476348 56.176533, 8.482252 56.177059, 8.482059 56.17622, 8.481894 56.175377, 8.481702 56.174142, 8.480291 56.174038, 8.480067 56.174175, 8.478484 56.175112, 8.476948 56.176049, 8.476754 56.176284, 8.476348 56.176533))"

    ############################## ------------- ##############################
    #                            API Key Information                          #
    ############################## ------------- ##############################
    api_key = "###########              REPLACE WITH API KEY              ###########"
    api_key = "SWxdjKp5o/9kRjYLvC7QqlTTulrtFhWhsH0uYfWaL5Q="

    api_service = ClearSkyVisionAPI(api_key)

    # Get information about API key
    apikey_info = api_service.get_api_key_info()

    assert apikey_info.Data is not None

    concurrent_requests = apikey_info.Data.MaxConcurrentConnections

    if len(required_bands) > apikey_info.Data.MaxTotalBands:
        raise Exception("too many bands for requests, reduce number of bands being retrieved")

    print(f"API key Maximum number of Concurrent Connections: {apikey_info.Data.MaxConcurrentConnections}")
    print(f"API key Maximum number of bands per request: {apikey_info.Data.MaxTotalBands} bands")
    print(f"API key Maximum area for composite imagery download per request: {apikey_info.Data.MaxCompositeAreaKm2} km2")
    print(f"API key Download Credit Limit, allowing for downloads being paid in arrears: {apikey_info.Data.CreditLimit} credits")
    print(f"API key Download Credits: {apikey_info.Data.CreditAmount} credits")
    print(f"API key Order Credit Limit, allowing for downloads being paid in arrears: {apikey_info.Data.EuroCreditLimit} credits")
    print(f"API key Order Credits: {apikey_info.Data.EuroCreditAmount} credits")

    ############################## ------------- ##############################
    #                            Composite Estimate                           #
    ############################## ------------- ##############################

    # allowed geographies (EPSG:4326 coordinates) for process composite are polygon and multipolygon
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
            Bandnames=required_bands,
        )

        estimate_dtos.append(dto)

    estimate_results = process_estimates(api_service, concurrent_requests, estimate_dtos)

    if any(index for index in estimate_results if not estimate_results[index][1].Succeeded):
        raise Exception("estimate failed: ")

    ############################## ------------- ##############################
    #                         Search Available Imagery                        #
    ############################## ------------- ##############################

    # allowed geographies (EPSG:4326 coordinates) for process composite are polygon and multipolygon

    estimate_dtos: List[models.ProcessCompositeEstimateQueryDto] = []

    search_dto = models.SearchAvailableImageryQueryDto(
        Wkt=test_wkt,
        From=date(2024, 11, 1),
        Until=date(2024, 11, 28),
    )

    search_imagery_available_result = api_service.search_available_imagery(search_dto)

    if not search_imagery_available_result.Succeeded:
        assert search_imagery_available_result.Error is not None

        issues: List[str] = [] if not isinstance(search_imagery_available_result.Data, Dict) else [issue for issue in search_imagery_available_result.Data.values()]

        raise Exception(search_imagery_available_result.Error.Message + " " + " ".join([", ".join(issue) for issue in issues]))

    assert isinstance(search_imagery_available_result.Data, models.SearchAvailableImageryData)
    available_imagery_dates = []

    for model in search_imagery_available_result.Data.ModelImageDates:
        dates_available = []
        if len(model.DatesByGeog) > 1:
            # we determine which dates are common between all elements in DatesByGeog, and allow use of those
            dates_by_geog = []
            for geog in model.DatesByGeog:
                dates_by_geog.append([datetime.strptime(datestr, "%Y-%m-%d").date() for datestr in geog.Dates])

            all_dates = set(geog_date for dates in dates_by_geog for geog_date in dates)
            for image_date in all_dates:
                geogs_with_date = sum(1 for dates in dates_by_geog if image_date in dates)
                if geogs_with_date == len(model.DatesByGeog):
                    dates_available.append(image_date)
        else:
            for geog in model.DatesByGeog:
                available_imagery_dates.extend([datetime.strptime(datestr, "%Y-%m-%d").date() for datestr in geog.Dates])

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
    #                                     Tasking                                 #
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
