from datetime import datetime, timedelta

from user import User
from polygon_api.search_polygon_api import Query
from polygon_api.download_polygon_api import request_data, request_estimate
import time

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="xxxxxxxxxxxxxxxxxxxxxx")
    show_progress = True # progress bar for each download

    from_date = datetime(year=2022, month=7, day=20)
    to_date = datetime(year=2022, month=7, day=21)
    bounding_box = "POLYGON((8.40470302590683 56.465968056026654,9.60221279153183 56.465968056026654,9.60221279153183 55.761573584491785,8.40470302590683 55.761573584491785,8.40470302590683 56.465968056026654))"
    resolution = 20  # 10, 20, 40, 50, 100, 200
    data_type = 'uint8'  # uint8 / uint16

    # Band options include ('rgb', 'all' or a combination of the following bands 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12')
    # It is also possible to pre calculate remote sensing indices in the form (Band1 - Band2) / (Band1 + Band2)
    # for instance NDVI would be written as [B8_B4] and will be calculated as (B8 - B4) / (B8 + B4)
    bands = 'B4, B3, B2, B8, [B8_B4]'


    out_folder = "C:/test/"
    file_type = 'tif'  # tif / png, if png is chosen datatype will be set to uint8 and bands will be set to rgb


    # For previews optimized for fast processing use the following settings: resolution = 50, data_type ='uint8' file_type = 'png'


    while from_date < to_date:

        file_name = "file_" + str(from_date).split(" ")[0].replace("-", "") + "." + file_type # This can be modified to suit your needs
        start = datetime.now()

        query = Query(bounding_box, str(from_date), resolution, data_type, bands, epsg_out, file_type)
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