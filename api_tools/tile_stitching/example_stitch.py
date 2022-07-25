from datetime import datetime, timedelta
from tile_stitching.stitching import stitch_tiles_in_folder, find_min_max_xy
from tile_stitching.tif_creator import save_geo_tiff

# stitch tiles in folder "data_path_out" and save as geotiff
# Currently this only works within one utm zone at a time
# this example is also only meant to be used with tile downloaded using the tile_API, and will need some customization if the default file names has been changed
def example_stitch():

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
    example_stitch()
