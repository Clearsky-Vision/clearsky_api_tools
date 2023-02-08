class Query():
    def __init__(self, bounding_box, date, resolution, bands, epsg_out, filetype):
        self.bounding_box = bounding_box
        self.date = date
        self.resolution = resolution
        self.bands = bands
        self.epsg_out = epsg_out
        self.datatype = 'uint16'
        self.filetype = filetype
