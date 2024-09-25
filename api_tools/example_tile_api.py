from datetime import datetime, timedelta
import requests
import os
from tqdm import tqdm
import json
import shutil
from pathlib import Path


# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    data_path_out = "destination-path"
    show_progress = True # progress bar for each download

    from_date = datetime(year=2023, month=8, day=26)
    to_date = datetime(year=2023, month=8, day=27)
    bounding_box = "POLYGON((8.903708128389857 55.28610673053661,9.205832151827357 55.28610673053661,9.205832151827357 55.09168156297725,8.903708128389857 55.09168156297725,8.903708128389857 55.28610673053661))"

    while from_date < to_date:

        query = Query(bounding_box, str(from_date).split(" ")[0] +"T00:00:00Z", str(from_date).split(" ")[0] +"T00:00:00Z")

        search_results = search_data(credentials, query)
        if not isinstance(search_results, list):
            print(str(search_results))
        else:
            download_all(search_results, data_path_out, credentials, show_progress)
        from_date += timedelta(days=1)

    print("done")


class User():
    def __init__(self, api_key):
        self.api_key = api_key


class Query():
    def __init__(self, bounding_box, start_date, end_date):
        self.bounding_box = bounding_box
        self.start_date = start_date
        self.end_date = end_date


def search_data(credentials, query):

    try:
        data_str = {"BoundingBoxWkt": query.bounding_box, "From": query.start_date, "Until": query.end_date}

        req = requests.post("https://api.clearsky.vision/api/satelliteimages/boundingbox/", json=data_str, timeout=200,headers={"X-API-KEY":credentials.api_key})
        print(f"Status Code: {req.status_code})#, Response: {req.json()}")
        if req.status_code == 200:
            return req.json()['Data']
        else:
            return req

    except Exception as E:
        return str(E)


def download_all(results, outpath, credentials, show_progress):

    count_area = 0
    for area in results:
        count_date = 0
        for date in area['SatelliteImageZones']:
            print("DL Progress --- Areas: " + str(count_area) + "/" + str(len(results)) + " dates: " + str(count_date) + "/" + str(len(area['SatelliteImageZones'])))
            url = "https://api.clearsky.vision/api/satelliteimages?satelliteImageId=" + str(date['SatelliteImageId'])
            name = outpath + str(area['Zone']) + "_" + str(area['XPosition']) + "-" + str(area['YPosition']) + "_" + str(date['ImageDate']).split("T")[0] + ".tif"
            if os.path.isfile(name):
                print("File already exists: " + name)
                count_date += 1
                continue
            download_raw_data(url, name, credentials, show_progress)
            count_date += 1
        count_area += 1


def download_raw_data(url, outfile, credentials, show_progress):

    outfile_temp = str(outfile) + ".incomplete"
    try:
        result = requests.get(url, stream=True, timeout=120,headers={"X-API-KEY":credentials.api_key})
        if result.status_code == 200:
            content = result.content
            content = content.decode('utf-8')
            content = json.loads(content)
            file_url = content['Data']['FileAzureSasUri']
        else:
            return

        downloaded_bytes = 0
        with requests.get(file_url, stream=True, timeout=800) as req:
            with tqdm(unit="B", unit_scale=True, disable=not show_progress) as progress:
                chunk_size = 2 ** 20
                with open(outfile_temp, "wb") as fout:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:
                            fout.write(chunk)
                            progress.update(len(chunk))
                            downloaded_bytes += len(chunk)
        shutil.move(outfile_temp, outfile)
    finally:
        try:
            Path(outfile_temp).unlink()
        except OSError:
            pass


if __name__ == '__main__':
    example_1() # Download tiles
