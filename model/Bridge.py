import salabim as sim

from model import GlobalVars, Utilities
from model.Node import Node
from model.Vessel import Vessel

closed = -1
open = +1


class Bridge(Node, sim.Component):
    """Defines a bridge on a fairway"""

    open_time = 5
    pass_time = 1

    def __init__(self, fw_code, coordinates_pair):
        Node.__init__(self, coordinates_pair[0], coordinates_pair[1])
        self.fw_code = fw_code
        self.left = None
        self.right = None
        self.state = closed
        self.key_in = None

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
        sim.Component.__init__(self)
        coordinate = (self.x, self.y)
        neighbors = list(graph.neighbors(coordinate))
        if len(neighbors) != 2:
            print("Well well well, WE ARE FUCKED")

        self.left = neighbors[0]
        self.right = neighbors[1]
        self.key_in = sim.Resource(name="Bridge at " + str(coordinate) + " => key in")

    def process(self):
        yield self.request(self.key_in)

        while True:
            if len(self.key_in.requesters()) == 0:
                yield self.passivate()

            yield self.hold(self.open_time)
            self.release(self.key_in)
            self.state = -self.state
            yield self.hold(10)
            yield self.request(self.key_in)
            yield self.hold(self.open_time)
            self.state = -self.state

    def check_fit(self, vessel: Vessel) -> bool:
        if self.state == open:
            return True
        else:
            return False
