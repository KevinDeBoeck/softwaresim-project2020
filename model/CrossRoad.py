import salabim as sim

from model import Utilities, GlobalVars
from model.Node import Node


class CrossRoad(Node):
    def __init__(self, coordinates_pair):
        super().__init__(coordinates_pair[0], coordinates_pair[1])
        self.intersections = {}
        self.claim = sim.Resource()

    def draw(self):
        coordinate_tuple = Utilities.normalize(self.x, self.y)
        size = 2
        if GlobalVars.zoom:
            size = size / 2
        self.animate = sim.AnimatePoints(spec=coordinate_tuple, linecolor='red', linewidth=size, layer=3)
