import salabim as sim
import simulation


class Bridge(object):
    """Defines a bridge"""

    def __init__(self, properties, lon, lat):
        self.properties = properties
        self.lon = lon
        self.lat = lat
        self.projected_lon = lon
        self.projected_lat = lat
        self.animate = None

    def draw(self):
        draw_scale = simulation.draw_scale
        self.animate = sim.AnimateCircle(radius=0.005, x=self.projected_lon * draw_scale,
                                         y=self.projected_lat * draw_scale,
                                         fillcolor="lime")
