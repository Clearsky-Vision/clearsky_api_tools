from datetime import datetime, timedelta

from user import User
from polygon_api.search_polygon_api import Query
from polygon_api.download_polygon_api import request_data, request_estimate
import time

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="xxxxxxxxxxxxxxxxxxxxxxxxx")
    show_progress = True # progress bar for each download
    out_folder = "C:/test/"

    from_date = datetime(year=2019, month=3, day=1)
    to_date = datetime(year=2022, month=1, day=1)
    bounding_box = "POLYGON((-60.00686304081232 -12.366792901186335,-50.31692163456232 -12.366792901186335,-50.31692163456232 -18.505618971723774,-60.00686304081232 -18.505618971723774,-60.00686304081232 -12.366792901186335))"
    resolution = 10  # 10, 20, 40, 50, 100, 200
    epsg_out = 32632  # any epsg number # for original utmzone # 326 + zone eg. 32632 (denmark)

    # Band options include ('rgb', 'all' or a combination of the following bands 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12')
    # It is also possible to pre calculate remote sensing indices in the form (Band1 - Band2) / (Band1 + Band2)
    # for instance NDVI would be written as [B8_B4] and will be calculated as (B8 - B4) / (B8 + B4)
    bands = 'B4, B3, B2, B8, [B8_B4]'


    while from_date < to_date:

        file_name = "file_" + str(from_date).split(" ")[0].replace("-", "") + ".tif"  # This can be modified to suit your needs
        start = datetime.now()

        query = Query(bounding_box, str(from_date), resolution, bands, epsg_out)
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
        if new_file_path is None:
            print("request failed")
        from_date += timedelta(days=1)

    print("done")



if __name__ == '__main__':
    example_1()