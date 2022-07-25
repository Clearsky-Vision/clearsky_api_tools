from datetime import datetime, timedelta

from user import User
from search import Query
from polygon_api.download import request_data, request_estimate

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="xxxxxx")
    show_progress = True # progress bar for each download

    from_date = datetime(year=2022, month=7, day=6)
    to_date = datetime(year=2022, month=7, day=7)
    bounding_box = "POLYGON((8.40470302590683 56.465968056026654,9.60221279153183 56.465968056026654,9.60221279153183 55.761573584491785,8.40470302590683 55.761573584491785,8.40470302590683 56.465968056026654))"
    resolution = 10  # 10, 20, 40, 50, 100, 200
    data_type = 'uint16'  # uint8 / uint16
    bands = 'all'  # all / rgb
    epsg_out = 3857  # any epsg number # for original utmzone # 326 + zone eg. 32632 (denmark)
    file_type = 'tif'  # tif / png
    out_folder = "C:/test/"


    while from_date < to_date:

        file_name = "file_" + str(from_date).split(" ")[0].replace("-", "") + "." + file_type
        start = datetime.now()
        query = Query(bounding_box, str(from_date), resolution, data_type, bands, epsg_out, file_type)
        resp = request_estimate(query)
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