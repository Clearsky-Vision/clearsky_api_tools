import requests
from tqdm import tqdm
import shutil
from pathlib import Path

def download_all(query, outpath, credentials, show_progress, filename):


    url = "https://api.clearsky.vision/api/SatelliteImages/preview/boundingbox?boundingBox=" + query.bounding_box + \
          "&date=" + query.date + "&resolution=" + str(query.resolution) +"&epsgProjection=" + str(query.epsg_out) + "&Datatype=" + \
          str(query.data_type) + "&bandNames=" + query.bands + "&FileType=" + query.file_type


    name = outpath + filename

    download_raw_data(url, name, credentials, show_progress)

def download_raw_data(url, outfile, credentials, show_progress):

    outfile_temp = str(outfile) + ".incomplete"
    try:
        downloaded_bytes = 0
        with requests.get(url, stream=True, timeout=800,headers={"X-API-KEY":credentials.api_key}) as req:
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