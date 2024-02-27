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

    credentials = User(api_key="xxxxxxxxxxxxxxxxxxx")
    show_progress = True # progress bar for each download
    out_folder = "destination_path"

    from_date = datetime(year=2023, month=11, day=1)
    to_date = datetime(year=2023, month=11, day=10)


    #use a geojson or wkt to define an area, but only one of them, the other must be None
    bounding_box = "POLYGON ((9.162598 56.14555, 9.162598 56.413901, 9.624023 56.413901, 9.624023 56.14555, 9.162598 56.14555))"
    geojson_path = None # "example_gjson.geojson"


    resolution = 10  # 10, 20, 40, 80, 160, 320
    epsg_out = 3857  # any epsg number # for original utmzone # 326 + zone eg. 32632 (denmark)
    filetype = 'tif'  # 'tif' or 'png'

    pixel_selection_mode = 'intersect' # Intersect or Contained
    data_type = 'int16' # int16 or uint8
    utm_data_selection_mode = 'combined_utm' # single_utm_fully_covered, single_utm, combined_utm


    # Band options include ('original' for all bands or a combination of the following bands 'B2_original', 'B3_original', 'B4_original', 'B5_original', 'B6_original', 'B7_original', 'B8_original', 'B8A_original', 'B11_original', 'B12_original')
    bands = 'B4_original, B3_original, B2_original'

    while from_date < to_date:
        
        file_name = "Sentinel2_original_" + str(from_date).split(" ")[0].replace("-", "") + ".tif"  # Modify to suit your needs
        start = datetime.now()

        query = Query(bounding_box, str(from_date), resolution, bands, epsg_out, filetype, geojson_path, pixel_selection_mode, data_type, utm_data_selection_mode)

        resp = request_estimate(query)
        if resp is None: # Server unreachable / invalid request parameters
            wait_seconds = 5 # time to wait before trying again
            print("Retrying in " + str(wait_seconds) + " seconds")
            time.sleep(wait_seconds)
            continue
        print("Job credit cost: " + str(resp['Data']['CreditEstimate']) + " credits" + ", Job processing time ~ " + str(resp['Data']['FastTimeEstimateSeconds']) + " to " + str(resp['Data']['SlowTimeEstimateSeconds']) + " Seconds")
        print("Job output area: " + str(resp['Data']['AreaEstimateKm2']) + "Km2" + ", Estimated file size:" + str(resp['Data']['FileSizeEstimateMB']) + "mb")

        new_file_path = request_data(query, out_folder, credentials, show_progress, file_name, start)

        # if request failed
        if new_file_path[0] is None:
            print("request failed")
        from_date += timedelta(days=1)

    print("done")




class Query():
    def __init__(self, bounding_box, date, resolution, bands, epsg_out, filetype, geojson_path, pixel_selection_mode, data_type, utm_data_selection_mode):
        self.bounding_box = bounding_box
        self.date = date.split(" ")[0] +"T00:00:00Z"
        self.resolution = resolution
        self.bands = bands
        self.epsg_out = epsg_out
        self.datatype = data_type
        self.filetype = filetype
        self.pixel_selection_mode = pixel_selection_mode
        self.utm_data_selection_mode = utm_data_selection_mode



        if geojson_path is not None:
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
            self.geojson = None


class User():
    def __init__(self, api_key):
        self.api_key = api_key


def request_data(query, outpath, credentials, show_progress, filename, start):
    print("Server is now processing your request, please wait")
    sys.stdout.flush()

    url = "https://api.clearsky.vision/api/SatelliteProducts/process/composite/original"


    body = {"Date": query.date,
            "Resolution": query.resolution,
            "EpsgProjection": query.epsg_out,
            "FileType": query.filetype,
            "PixelSelectionMode": query.pixel_selection_mode,
            "DataType": query.datatype,
            "UtmDataSelectionMode": query.utm_data_selection_mode,
            "Bandnames": query.bands}
    
    if query.geojson is None:
        body["Wkt"] = query.bounding_box
    else:
        body["GeoJson"] = query.geojson

    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': credentials.api_key
    }

    out_file, processed_time = download_raw_data(url, outpath + filename, headers, body, show_progress, start)


    return out_file, processed_time

def request_estimate(query):


    url = "https://api.clearsky.vision/api/SatelliteProducts/process/composite/original/estimate"

    body = {
            "Date": query.date,
            "Resolution": query.resolution,
            "EpsgProjection": query.epsg_out,
            "FileType": query.filetype,
            "UtmDataSelectionMode": query.utm_data_selection_mode,
            "Bandnames": query.bands}
    
    if query.geojson is None:
        body["Wkt"] = query.bounding_box
    else:
        body["GeoJson"] = query.geojson

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
