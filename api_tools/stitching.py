import os
import numpy as np
import rasterio
import cv2

class Bounds():
    def __init__(self, epsg, min_lat, min_lon, max_lat, max_lon):
        self.epsg = epsg
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon

def find_min_max_xy(data_path, date, zone):

    files_tmp = os.listdir(data_path)
    files = []
    date = str(date).split(" ")[0]

    for i in range(0, len(files_tmp)):
        if date in files_tmp[i] and str(zone) + "_" in files_tmp[i]:
            files.append(files_tmp[i])

    min_x, min_y, max_x, max_y = find_min_max_pos(files)

    return min_x, min_y, max_x, max_y

def stitch_tiles_in_folder(data_path, date, zone, resolution=1, min_x=None, min_y=None, max_x=None, max_y=None, uint16=True):

    files_tmp = os.listdir(data_path)
    files = []
    date = str(date).split(" ")[0]

    for i in range(0, len(files_tmp)):
        if date in files_tmp[i] and str(zone) + "_" in files_tmp[i]:
            files.append(files_tmp[i])

    if min_x is None: # if no tile range specified, will then find min and max x and y in folder
        min_x, min_y, max_x, max_y = find_min_max_pos(files)

    im_size = int(1280*resolution)
    if uint16:
        full_image = np.zeros((10,((max_y-min_y)+1)*im_size,((max_x-min_x)+1)*im_size), dtype='uint16')
    else:
        full_image = np.zeros((10,((max_y-min_y)+1)*im_size,((max_x-min_x)+1)*im_size), dtype='float32')

    if len(files) < 1:
        return "No tiles available in search", None

    for i in range(0, len(files)):

        print(str(i) + "/" + str(len(files)))
        dataset = rasterio.open(data_path + files[i])
        aoi = dataset.bounds
        if i == 0:
            new_bounds = Bounds(dataset.crs.data['init'], min_lat=aoi.bottom, min_lon=aoi.left, max_lat=aoi.top, max_lon=aoi.right)
        else:
            new_bounds = update_bounds(aoi, new_bounds)
        x_pos, y_pos = files[i].split("_")[1].split("-")

        x_pos = int(x_pos) - min_x
        y_pos = max_y - int(y_pos)

        rescaled_image = dataset.read(

        )

        dim = (im_size, im_size)

        # resize image
        rescaled_image = rescaled_image.transpose((1,2,0))
        rescaled_image = cv2.resize(rescaled_image[:], dim, interpolation = cv2.INTER_AREA)
        rescaled_image = rescaled_image.transpose((2,0,1))
        if uint16:
            rescaled_image = float32_to_uint16(rescaled_image)

        full_image[:,y_pos*im_size:y_pos*im_size+im_size, x_pos*im_size:x_pos*im_size+im_size] = rescaled_image

    return full_image, new_bounds


def float32_to_uint16(input):
    multiplier = np.full(1, 65535, dtype='uint16')
    output = input * multiplier
    output = output.astype("uint16")
    return output

def update_bounds(aoi, bounds):

    if aoi.bottom < bounds.min_lat:
        bounds.min_lat = aoi.bottom
    if aoi.top > bounds.max_lat:
        bounds.max_lat = aoi.top
    if aoi.left < bounds.min_lon:
        bounds.min_lon = aoi.left
    if aoi.right > bounds.max_lon:
        bounds.max_lon = aoi.right

    return bounds

def find_min_max_pos(file_list):
    min_x = 9999
    min_y = 9999
    max_x = -9999
    max_y = -9999

    for i in range(0, len(file_list)):
        x_pos, y_pos = file_list[i].split("_")[1].split("-")
        if int(x_pos) < min_x:
            min_x = int(x_pos)
        if int(x_pos) > max_x:
            max_x = int(x_pos)
        if int(y_pos) < min_y:
            min_y = int(y_pos)
        if int(y_pos) > max_y:
            max_y = int(y_pos)

    return min_x, min_y, max_x, max_y