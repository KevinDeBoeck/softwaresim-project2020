import salabim as sim
from rectpack import newPacker, SORT_NONE, SkylineBl

from model import GlobalVars, Utilities
from model.Node import Node
from model.Vessel import Vessel

left = -1
right = +1


class Lock(Node, sim.Component):
    """Defines a lock on a fairway"""

    def __init__(self, fw_code, length, width, coordinates_pair):
        Node.__init__(self, coordinates_pair[0], coordinates_pair[1])
        self.fw_code = fw_code
        self.left = None
        self.right = None
        self.key_in = {}
        self.wait_in = {}
        self.key_out = None
        self.side = left
        self.length = length
        self.width = width

        self.packer = newPacker(sort_algo=SORT_NONE, pack_algo=SkylineBl, rotation=False)
        # GuillotineBssfSas

        self.packer.add_bin(self.width, self.length)
        self.packer.pack()

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
        self.animate = sim.AnimatePoints(spec=coordinate_tuple, linecolor='orangered', linewidth=size, layer=2)

    def init_node(self, graph):
        sim.Component.__init__(self)
        coordinate = (self.x, self.y)
        neighbors = list(graph.neighbors(coordinate))
        if len(neighbors) != 2:
            print("Well well well, WE ARE FUCKED")

        self.left = neighbors[0]
        self.right = neighbors[1]
        self.key_in[left] = sim.Resource(name="Lock at " + str(coordinate) + " => left key in")
        self.key_in[right] = sim.Resource(name="Lock at " + str(coordinate) + " => right key in")
        self.wait_in[left] = sim.Queue(name="Lock at " + str(coordinate) + " => left queue in")
        self.wait_in[right] = sim.Queue(name="Lock at " + str(coordinate) + " => right queue in")
        self.key_out = sim.Resource(name="Lock at " + str(coordinate) + " => key out")

    def process(self):
        for side in (left, right):
            yield self.request(self.key_in[side])
        yield self.request(self.key_out)

        while True:
            for vessel in self.wait_in[self.side]:
                vessel.activate()
            if len(self.wait_in[self.side]) == 0:
                if len(self.wait_in[-self.side]) == 0:
                    yield self.passivate()

            self.release(self.key_in[self.side])
            yield self.hold(GlobalVars.lock_wait_time, mode="Wait")
            yield self.request((self.key_in[self.side], 1, 1000))
            yield self.hold(GlobalVars.lock_switch_time, mode="Switch")
            self.side = -self.side
            self.release(self.key_out)
            yield self.request(self.key_out, mode="Wait")
            self.packer = newPacker(sort_algo=SORT_NONE, pack_algo=SkylineBl, rotation=False)
            self.packer.add_bin(self.width, self.length)
            self.packer.pack()

    def check_fit(self, vessel: Vessel) -> bool:
        if (len(self.packer.rect_list())) == 0:
            count = 0
        else:
            count = len(self.packer[0])
        self.packer.add_rect(vessel.width, vessel.length)
        self.packer.pack()
        if len(self.packer) > 0 and len(self.packer[0]) > count:
            return True
        else:
            return False
