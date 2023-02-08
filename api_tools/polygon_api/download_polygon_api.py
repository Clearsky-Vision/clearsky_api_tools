import requests
from tqdm import tqdm
import shutil
from pathlib import Path
import os
from datetime import datetime
import sys

def request_data(query, outpath, credentials, show_progress, filename, start):
    print("Server is now processing your request, please wait")
    sys.stdout.flush()

    url = "https://api.clearsky.vision/api/SatelliteImages/preview/boundingbox?boundingBox=" + query.bounding_box + \
          "&date=" + query.date + "&resolution=" + str(query.resolution) +"&epsgProjection=" + str(query.epsg_out) + "&bandNames=" + query.bands + "&Datatype=" + query.datatype + "&FileType=" + query.filetype


    name = outpath + filename

    out_file, processed_time = download_raw_data(url, name, credentials, show_progress, start)

    return out_file, processed_time

def request_estimate(query):


    url = "https://api.clearsky.vision/api/SatelliteImages/preview/boundingbox/estimate?boundingBox=" + query.bounding_box + \
          "&date=" + query.date + "&resolution=" + str(query.resolution) + "&bandNames=" + query.bands  + "&dataType=" + query.datatype + "&fileType=" + query.filetype


    #name = outpath + filename
    resp = requests.get(url)

    #out_file, processed_time = download_raw_data(url, name, credentials, show_progress)

    if resp.status_code == 200:
        return resp.json()
    else:
        print("Your request for a job estimate has failed, please try again (possibly invalid parameters)")

def download_raw_data(url, outfile, credentials, show_progress, start):
    processed_time = None
    outfile_temp = str(outfile) + ".incomplete"
    try:
        downloaded_bytes = 0
        with requests.get(url, stream=True, timeout=3000,headers={"X-API-KEY":credentials.api_key}) as req:
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
        if downloaded_bytes < 1000: # something went wrong
            with open(outfile, "r") as f_in:
                lines = f_in.readlines()
            os.remove(outfile)

            print("Download failed, with response: " + lines[0])
            return None, processed_time
    except Exception as E:
        print("download failed")
        return None, processed_time
    finally:
        try:
            Path(outfile_temp).unlink()
        except OSError:
            pass

    return outfile, processed_time