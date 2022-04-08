import requests
from tqdm import tqdm
import shutil
from pathlib import Path
import os

def download_all(results, outpath, credentials):

    count_area = 0
    for area in results:
        count_date = 0
        for date in area['SatelliteImageZones']:
            url = "https://api.clearsky.vision/api/satelliteimages?satelliteImageId=" + str(date['SatelliteImageId'])
            name = outpath + "32_" + str(area['XPosition']) + "-" + str(area['YPosition']) + "_" + str(date['ImageDate']).split("T")[0] + ".tif"
            if os.path.isfile(name):
                print("File already exists: " + name)
                count_date += 1
                continue
            download_raw_data(url, name, credentials, True)
            print("DL Progress --- Areas: " + str(count_area) + "/" + str(len(results)) + " dates: " + str(count_date) + "/" + str(len(area['SatelliteImageZones'])))
            count_date += 1
        count_area += 1


def download_raw_data(url, outfile, credentials, show_progress):
    """Downloads data from url to outfile.incomplete and then moves to outfile"""
    outfile_temp = str(outfile) + ".incomplete"
    try:
        downloaded_bytes = 0
        with requests.get(url, stream=True, timeout=100,headers={"X-API-KEY":credentials.api_key}) as req:
            with tqdm(unit="B", unit_scale=True, disable=not show_progress) as progress:
                chunk_size = 2 ** 20  # download in 1 MB chunks
                with open(outfile_temp, "wb") as fout:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive new chunks
                            fout.write(chunk)
                            progress.update(len(chunk))
                            downloaded_bytes += len(chunk)
        shutil.move(outfile_temp, outfile)
    finally:
        try:
            Path(outfile_temp).unlink()
        except OSError:
            pass