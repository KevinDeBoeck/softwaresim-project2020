import numpy as np
import salabim as sim

from model import GlobalVars, Utilities
from model.Node import Node


class FairwaySection:
    """Defines a single fairway section"""

    def __init__(self, fw_code, set_of_coordinate_pairs):
        self.nodes = []
        self.bridges = []
        self.locks = []
        self.fw_code = fw_code
        GlobalVars.fairway_section_dict[self.fw_code] = self

        tmp = []
        for coordinate_pairs in set_of_coordinate_pairs:
            for coordinates in coordinate_pairs:
                coordinates_tuple = (coordinates[0],coordinates[1])
                if coordinates_tuple not in tmp:
                    tmp.append(coordinates_tuple)

        for coordinates in tmp:
            lon = coordinates[0]
            lat = coordinates[1]

            x, y = lon, lat

            node = Node(x, y)
            GlobalVars.node_x_min = min(x, GlobalVars.node_x_min)
            GlobalVars.node_x_max = max(x, GlobalVars.node_x_max)
            GlobalVars.node_y_min = min(y, GlobalVars.node_y_min)
            GlobalVars.node_y_max = max(y, GlobalVars.node_y_max)

            self.nodes.append(node)

    def draw(self):
        fairway_arr = np.array([[Utilities.normalize(node.x, node.y)] for node in self.nodes])

        # Make this a one-dimensional array (so we can generate a tuple easily)
        fairway_arr = fairway_arr.ravel()
        # Make a tuple (accepted by the 'AnimatePoints' function
        fairway_tuple = tuple(fairway_arr)
        # Draw all the fairway points on the map
        size = 1
        if GlobalVars.zoom:
            size = size / 2
        sim.AnimateLine(spec=fairway_tuple, linewidth=size, linecolor='blue', layer=4)

        for node in self.nodes:
            node.draw()
