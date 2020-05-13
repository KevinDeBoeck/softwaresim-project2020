import math

import salabim as sim

from model import GlobalVars, Utilities
from model.Node import Node
from model.Vessel import Vessel, VesselComponent

closed = -1
open = +1


class Bridge(Node, sim.Component):
    """Defines a bridge on a fairway"""

    def __init__(self, fw_code, movable, height, coordinates_pair):
        Node.__init__(self, coordinates_pair[0], coordinates_pair[1])
        self.fw_code = fw_code
        self.left = None
        self.right = None
        self.state = closed
        self.order = None
        self.moving = None
        self.movable = movable
        if height is None or math.isnan(height):
            height = 0
        self.height = height / 100

        # Get the fairway section this belongs to
        if self.fw_code not in GlobalVars.fairway_section_dict:
            print("We have problem here..")

        insertion_idx = -1
        min_distance = float('inf')

        fairway_section = GlobalVars.fairway_section_dict.get(self.fw_code)
        for idx, fairway_section_node in enumerate(fairway_section.nodes):
            distance = Utilities.haversine([self.y, self.x], [fairway_section_node.y, fairway_section_node.x])
            if distance < min_distance:
                min_distance = distance
                insertion_idx = idx

        if min_distance == 0:
            fairway_section.nodes[insertion_idx] = self
        else:
            # Append add the best index
            if insertion_idx >= len(fairway_section.nodes) - 1:
                insertion_idx = insertion_idx - 1

            fairway_section.nodes.insert(insertion_idx + 1, self)

    def draw(self):
        coordinate_tuple = Utilities.normalize(self.x, self.y)
        size = 1
        if GlobalVars.zoom:
            size = size / 2
        self.animate = sim.AnimatePoints(spec=coordinate_tuple, linecolor='lime', linewidth=size, layer=0)

    def init_node(self, graph):
        if self.useful:
            sim.Component.__init__(self)
            coordinate = (self.x, self.y)
            neighbors = list(graph.neighbors(coordinate))
            if len(neighbors) != 2:
                print("Well well well, WE ARE FUCKED")

            self.left = neighbors[0]
            self.right = neighbors[1]
            self.order = sim.Resource(name="Bridge at " + str(coordinate) + " => order")
            self.moving = sim.Resource(name="Bridge at " + str(coordinate) + " => moving")

    def process(self):
        if self.movable:

            while GlobalVars.num_vessels_failed + GlobalVars.num_vessels_finished != GlobalVars.num_vessels:
                if len(self.order.requesters()) == 0:
                    yield self.passivate()

                yield self.request((self.moving, 1, 1000))
                yield self.hold(GlobalVars.bridge_open_time)
                self.release(self.moving)
                self.state = -self.state
                yield self.hold(GlobalVars.bridge_min_wait)
                yield self.request((self.moving, 1, 1000))
                yield self.hold(GlobalVars.bridge_open_time)
                self.release(self.moving)
                self.state = -self.state
        else:
            self.state = open

    def check_fit(self, vessel: VesselComponent) -> bool:
        if self.state == open or not self.movable or vessel.vessel.height < self.height:
            return True
        else:
            return False

    def check_fit_closed(self, vessel: VesselComponent) -> bool:
        if not self.movable or vessel.vessel.height < self.height:
            return True
        else:
            return False
