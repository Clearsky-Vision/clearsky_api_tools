import os
from osgeo import gdal, osr

def save_geo_tiff(data, bounds, save_path, file_name, uint16=True):

    nx = data.shape[2]
    ny = data.shape[1]
    xmin, ymin, xmax, ymax = [bounds.min_lon, bounds.min_lat, bounds.max_lon, bounds.max_lat]

    xres = (xmax - xmin) / float(nx)
    yres = (ymax - ymin) / float(ny)

    geotransform = (xmin, xres, 0, ymax, 0, -yres)

    if not os.path.exists(save_path + "/"):
        os.makedirs(save_path + "/")

    if uint16:
        tif_out = gdal.GetDriverByName('GTiff').Create(save_path + file_name + '.tif', nx, ny, 10, gdal.GDT_Int16)
    else:
        tif_out = gdal.GetDriverByName('GTiff').Create(save_path + file_name + '.tif', nx, ny, 10, gdal.GDT_Float32)

    tif_out.SetGeoTransform(geotransform)    # specify coords
    srs = osr.SpatialReference()
    crs = int(bounds.epsg.split(":")[1])
    srs.ImportFromEPSG(crs)
    wkt = srs.ExportToWkt()
    tif_out.SetProjection(wkt)

    add_band(data[0], 'B2', 1, tif_out)
    add_band(data[1], 'B3', 2, tif_out)
    add_band(data[2], 'B4', 3, tif_out)
    add_band(data[3], 'B5', 4, tif_out)
    add_band(data[4], 'B6', 5, tif_out)
    add_band(data[5], 'B7', 6, tif_out)
    add_band(data[6], 'B8', 7, tif_out)
    add_band(data[7], 'B8A', 8, tif_out)
    add_band(data[8], 'B11', 9, tif_out)
    add_band(data[9], 'B12', 10, tif_out)

    tif_out.FlushCache()                 # write to disk
    tif_out = None
    print("geoTiffSaved")


def add_band(band, band_name, band_number, tif_out):
    RasterBand = tif_out.GetRasterBand(band_number)
    RasterBand.SetNoDataValue(0)
    RasterBand.SetDescription(band_name)
    RasterBand.WriteArray(band)
