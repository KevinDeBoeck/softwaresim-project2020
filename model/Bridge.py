import salabim as sim

from model import GlobalVars, Utilities
from model.Node import Node


class Bridge(Node):
    """Defines a bridge on a fairway"""

    def __init__(self, fw_code, coordinates_pair):
        super().__init__(coordinates_pair[0], coordinates_pair[1])
        self.fw_code = fw_code

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
