from datetime import datetime, timedelta
from user import User
from search import Query
from download import download_all

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="")
    show_progress = True # progress bar for each download

    from_date = datetime(year=2022, month=4, day=7)
    to_date = datetime(year=2022, month=4, day=8)
    bounding_box = "POLYGON((-3.1581414092067095 52.92416473659307,-0.9828484404567095 52.92416473659307,-0.9828484404567095 51.00203044830556,-3.1581414092067095 51.00203044830556,-3.1581414092067095 52.92416473659307))"
    resolution = 20  # 10, 20, 40, 50, 100, 200
    data_type = 'uint8'  # uint8 / uint16
    bands = 'rgb'  # all / rgb
    epsg_out = 3857  #website projection 3857 any epsg number wgs84 4326 # for original utmzone # 326 + zone eg. 32632 (denmark),  32630 (UK)
    file_type = 'png'  # tif / png
    out_folder = "C:/test/"


    while from_date < to_date:

        file_name = "file_" + str(from_date).split(" ")[0].replace("-", "") + "." + file_type

        query = Query(bounding_box, str(from_date), resolution, data_type, bands, epsg_out, file_type)

        download_all(query, out_folder, credentials, show_progress, file_name)
        from_date += timedelta(days=1)

    print("done")



if __name__ == '__main__':
    example_1()
