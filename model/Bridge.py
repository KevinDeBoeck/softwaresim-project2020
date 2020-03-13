class Bridge(object):
    """Defines a bridge"""

    def __init__(self, properties, lon, lat):
        self.properties = properties
        self.lon = lon
        self.lat = lat
        self.projected_lon = lon
        self.projected_lat = lat

    def animate(self):
        print()