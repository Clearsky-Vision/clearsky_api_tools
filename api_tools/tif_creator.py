import os
from rasterio.transform import from_origin
import rasterio
from rasterio.crs import CRS


def save_geo_tiffRast(data, bounds, save_path, file_name, uint16=True):

    if not os.path.exists(save_path + "/"):
        os.makedirs(save_path + "/")

    nx = data.shape[2]
    ny = data.shape[1]
    xmin, ymin, xmax, ymax = [bounds.min_lon, bounds.min_lat, bounds.max_lon, bounds.max_lat]

    xres = (xmax - xmin) / float(nx)
    yres = (ymax - ymin) / float(ny)

    transform = from_origin(xmin, ymax, xres, yres)
    crs = int(bounds.epsg.split(":")[1])
    crs = CRS.from_epsg(crs)
    if uint16:
        profile_settings = {'dtype': 'uint16',
                            'nodata': 0,
                            'driver': 'GTiff',
                            'interleave': 'band',
                            'tiled': True,
                            'blockxsize': 256,
                            'blockysize': 256,
                            'compress': 'lzw'}
    else:
        profile_settings = {'dtype': 'float32',
                            'nodata': 0,
                            'driver': 'GTiff',
                            'interleave': 'band',
                            'tiled': True,
                            'blockxsize': 256,
                            'blockysize': 256,
                            'compress': 'lzw'}


    new_dataset = rasterio.open(save_path + file_name + '.tif', 'w', **profile_settings,
                                height = data.shape[1], width = data.shape[2],
                                count=10,
                                crs=crs,
                                transform=transform)

    new_dataset.write(data[0], 1)
    new_dataset.write(data[1], 2)
    new_dataset.write(data[2], 3)
    new_dataset.write(data[3], 4)
    new_dataset.write(data[4], 5)
    new_dataset.write(data[5], 6)
    new_dataset.write(data[6], 7)
    new_dataset.write(data[7], 8)
    new_dataset.write(data[8], 9)
    new_dataset.write(data[9], 10)
    new_dataset.set_band_description(1, "B2")
    new_dataset.set_band_description(2, "B3")
    new_dataset.set_band_description(3, "B4")
    new_dataset.set_band_description(4, "B5")
    new_dataset.set_band_description(5, "B6")
    new_dataset.set_band_description(6, "B7")
    new_dataset.set_band_description(7, "B8")
    new_dataset.set_band_description(8, "B8A")
    new_dataset.set_band_description(9, "B11")
    new_dataset.set_band_description(10, "B12")
    new_dataset.close()

    print("geoTiffSaved")

def add_band(band, band_name, band_number, tif_out):
    RasterBand = tif_out.GetRasterBand(band_number)
    RasterBand.SetNoDataValue(0)
    RasterBand.SetDescription(band_name)
    RasterBand.WriteArray(band)
