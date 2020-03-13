import salabim as sim

import simulation


class CrossRoad(object):
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat
        self.animate = None
        self.intersections = {}

    def draw(self):
        draw_scale = simulation.draw_scale
        self.animate = sim.AnimateCircle(radius=0.01, x=self.lon * draw_scale,
                                         y=self.lat * draw_scale,
                                         fillcolor="red")
