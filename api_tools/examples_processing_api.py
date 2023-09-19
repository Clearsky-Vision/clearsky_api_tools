from datetime import datetime, timedelta
import time
import requests
import sys
import os
import shutil
from pathlib import Path
from tqdm import tqdm
import json

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="XXXXXXXXXXXXXXXXXXXXXXXXXX")
    show_progress = True # progress bar for each download
    out_folder = "destination-path"

    from_date = datetime(year=2023, month=8, day=26)
    to_date = datetime(year=2023, month=8, day=27)



    #use a geojson or wkt to define an area, but only one of them
    use_geojson = False
    bounding_box = "POLYGON((8.903708128389857 55.28610673053661,9.205832151827357 55.28610673053661,9.205832151827357 55.09168156297725,8.903708128389857 55.09168156297725,8.903708128389857 55.28610673053661))"
    geojson_path = "example_gjson.geojson"


    resolution = 40  # 10, 20, 40, 50, 100, 200
    epsg_out = 3857  # any epsg number # for original utmzone # 326 + zone eg. 32632 (denmark)
    filetype = 'tif'  # 'tif' or 'png'


    # Band options include ('rgb', 'all' or a combination of the following bands 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12')
    # It is also possible to pre-compute remote sensing indices in the form (Band1 - Band2) / (Band1 + Band2)
    # for instance NDVI would be written as [B8_B4] and will be calculated as (B8 - B4) / (B8 + B4)
    bands = 'all'#'B2, B3, B4,[B8_B4]'

    while from_date < to_date:

        file_name = "Sentinel2ClearSky_" + str(from_date).split(" ")[0].replace("-", "") + ".tif"  # Modify to suit your needs
        start = datetime.now()

        query = Query(bounding_box, str(from_date), resolution, bands, epsg_out, filetype, geojson_path)

        resp = request_estimate(query, use_geojson)
        if resp is None: # Server unreachable / invalid request parameters
            wait_seconds = 5 # time to wait before trying again
            print("Retrying in " + str(wait_seconds) + " seconds")
            time.sleep(wait_seconds)
            continue
        print("Job credit cost: " + str(resp['Data']['CreditEstimate']) + " credits" + ", Job processing time ~ " + str(resp['Data']['FastTimeEstimateSeconds']) + " to " + str(resp['Data']['SlowTimeEstimateSeconds']) + " Seconds")
        print("Job output area: " + str(resp['Data']['AreaEstimateKm2']) + "Km2" + ", Estimated file size:" + str(resp['Data']['FileSizeEstimateMB']) + "mb")

        new_file_path = request_data(query, out_folder, credentials, show_progress, file_name, start, use_geojson)

        # if request failed
        if new_file_path[0] is None:
            print("request failed")
        from_date += timedelta(days=1)

    print("done")




class Query():
    def __init__(self, bounding_box, date, resolution, bands, epsg_out, filetype, geojson_path):
        self.bounding_box = bounding_box
        self.date = date.split(" ")[0] +"T00:00:00Z"
        self.resolution = resolution
        self.bands = bands
        self.epsg_out = epsg_out
        self.datatype = 'uint16'
        self.filetype = filetype

        if geojson_path != "":
            with open(geojson_path, 'r', encoding='utf-8-sig') as file:
                geojson_file = json.load(file)

            if geojson_file['type'] == 'FeatureCollection':
                polygon_geometries = [
                    feature['geometry'] for feature in geojson_file['features']
                    if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']
                ]
            elif geojson_file['type'] in ['Polygon', 'MultiPolygon']:
                polygon_geometries = [geojson_file]
            if len(polygon_geometries) > 1:
                print("warning multiple polygons/multipolygons detected, only first is used")
            self.geojson = polygon_geometries[0]

        else:
            self.geojson = ""


class User():
    def __init__(self, api_key):
        self.api_key = api_key


def request_data(query, outpath, credentials, show_progress, filename, start, use_geojson):
    print("Server is now processing your request, please wait")
    sys.stdout.flush()

    url = "https://api.clearsky.vision/api/SatelliteImages/process/composite"

    # Create the payload for POST request from the provided 'query' object
    if use_geojson == False:
        body = {
            "Wkt": query.bounding_box,
            "Date": query.date,
            "Resolution": query.resolution,
            "EpsgProjection": query.epsg_out,
            "FileType": query.filetype,
            "Bandnames": query.bands
            # Add any other required fields
        }
    else:
        body = {
            "GeoJson": query.geojson,
            "Date": query.date,
            "Resolution": query.resolution,
            "EpsgProjection": query.epsg_out,
            "FileType": query.filetype,
            "Bandnames": query.bands
            # Add any other required fields
        }

    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': credentials.api_key
    }

    out_file, processed_time = download_raw_data(url, outpath + filename, headers, body, show_progress, start)


    return out_file, processed_time

def request_estimate(query, use_geojson):


    url = "https://api.clearsky.vision/api/SatelliteImages/process/composite/estimate"

    # Create the payload for POST request from the provided 'query' object
    if use_geojson == False:
        body = {
            "Wkt": query.bounding_box,
            "Date": query.date,
            "Resolution": query.resolution,
            "FileType": query.filetype,
            "Bandnames": query.bands
            # Add any other required fields
        }
    else:
        body = {
            "GeoJson": query.geojson,
            "Date": query.date,
            "Resolution": query.resolution,
            "FileType": query.filetype,
            "Bandnames": query.bands
            # Add any other required fields
        }

    resp = requests.post(url, json=body)

    if resp.status_code == 200:
        return resp.json()
    else:
        print(resp.content)



def download_raw_data(url, outfile, headers, body, show_progress, start):
    processed_time = None
    outfile_temp = str(outfile) + ".incomplete"
    try:
        downloaded_bytes = 0
        # Using POST request here
        with requests.post(url, headers=headers, json=body, stream=True, timeout=3000) as req:
            with tqdm(unit="B", unit_scale=True, disable=not show_progress) as progress:
                chunk_size = 2 ** 20
                with open(outfile_temp, "wb") as fout:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:
                            if processed_time is None:
                                processed_time = datetime.now()
                                print("Processing finished, time elapsed: " + str((processed_time - start).seconds) + " seconds, starting download")
                            fout.write(chunk)
                            progress.update(len(chunk))
                            downloaded_bytes += len(chunk)
        shutil.move(outfile_temp, outfile)
        if downloaded_bytes < 1000:  # something went wrong
            with open(outfile, "r") as f_in:
                lines = f_in.readlines()
            os.remove(outfile)

            print("Download failed, with response: " + lines[0])
            return None, processed_time
    except Exception as E:
        print("Download failed:", E)
        return None, processed_time
    finally:
        try:
            Path(outfile_temp).unlink()
        except OSError:
            pass

    return outfile, processed_time

if __name__ == '__main__':
    example_1()