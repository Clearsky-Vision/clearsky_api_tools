class Query():
    def __init__(self, bounding_box, date, resolution, data_type, bands, epsg_out, file_type):
        self.bounding_box = bounding_box
        self.date = date
        self.resolution = resolution
        self.data_type = data_type
        self.bands = bands
        self.epsg_out = epsg_out
        self.file_type = file_type