from datetime import datetime, timedelta
from stitching import stitch_tiles_in_folder, find_min_max_xy
from tif_creator import save_geo_tiff
from user import User
from search import Query, search_data
from download import download_all

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="XXXXXXXXXXXXXXXXXXXXXXXX")

    data_path_out = "C:/Clearsky/tiles/"
    show_progress = False # progress bar for each download

    from_date = datetime(year=2022, month=3, day=23)
    to_date = datetime(year=2022, month=3, day=24)
    bounding_box = "POLYGON((9.44157475367803 56.23087158612058,9.90300053492803 56.23087158612058,9.90300053492803 55.98582291169851,9.44157475367803 55.98582291169851,9.44157475367803 56.23087158612058))"

    while from_date < to_date:

        query = Query(bounding_box, str(from_date).split(" ")[0] +"T00:00:00Z", str(from_date).split(" ")[0] +"T00:00:00Z")

        search_results = search_data(credentials, query)
        if not isinstance(search_results, list):
            print(str(search_results))
        else:
            download_all(search_results, data_path_out, credentials, show_progress)
            from_date += timedelta(days=1)

    print("done")

# stitch tiles in folder "data_path_out" and save as geotiff
# Currently this only works within one utm zone at a time
def example_2():

    data_path_in = "C:/Clearsky/tiles/" #Location of downloaded tiles
    date = datetime(year=2022, month=3, day=23)
    zone = 32 # utm zone to use
    uint16 = True # if false, will keep data in float32
    out_name = "test"
    output_resolution = 0.2 #1 for 10m, 0.5 for 20m, 0.2 for 50m...
    data_path_out = "C:/Clearsky/stitched/"


    #Finds max x and y pos for specified utm zone in data_path_in folder for a specific day
    min_x, min_y, max_x, max_y = find_min_max_xy(data_path_in, date, zone)

    # stitches tiles between tile pos min and max x and y. Pick your own min and max xy to avoid using all tiles in data folder
    new_tile, new_bounds = stitch_tiles_in_folder(data_path_in, date, zone, uint16=uint16, resolution=output_resolution,
                                                  min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    save_geo_tiff(new_tile, new_bounds, data_path_out, out_name, uint16=uint16)


    print("done")



if __name__ == '__main__':
    example_1()
    #example_2()