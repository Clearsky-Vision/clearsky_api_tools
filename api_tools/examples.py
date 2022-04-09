from datetime import datetime, timedelta
from stitching import stitch_tiles_in_folder
from tif_creator import save_geo_tiff, save_geo_tiffRast
from user import User
from search import Query, search_data
from download import download_all

# download all files in search to folder
def example_1():

    data_path = "C:/data/in/"
    credentials = User(api_key="*****************")

    from_date = datetime(year=2022, month=4, day=4)
    to_date = datetime(year=2022, month=4, day=5)

    bounding_box = "POLYGON((6.162480642310713 58.08939332219047,14.819707204810712 58.08939332219047,14.819707204810712 47.23436188677689,6.162480642310713 47.23436188677689,6.162480642310713 58.08939332219047))"

    while from_date < to_date:

        query = Query(bounding_box, str(from_date).split(" ")[0] +"T00:00:00Z", str(from_date).split(" ")[0] +"T00:00:00Z")

        search_results = search_data(credentials, query)
        download_all(search_results, data_path, credentials)

        from_date += timedelta(days=1)

    print("done")




# stitch tiles in folder "data_path" and save as geotiff
def example_2():

    data_path = "C:/data/in/"
    date = datetime(year=2022, month=3, day=27)
    zone = 32 # utm zone to use
    uint16 = True # if false, will keep data in float32
    out_name = "test"
    out_path = "C:/data/out/"

    new_tile, new_bounds = stitch_tiles_in_folder(data_path, date, zone, uint16=uint16, resolution=0.2) # Set min_x, min_y, max_x, max_y to limit the area

    save_geo_tiffRast(new_tile, new_bounds, out_path, out_name, uint16=uint16)


    print("done")



if __name__ == '__main__':
  #  example_1()
    example_2()