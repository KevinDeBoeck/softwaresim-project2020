from enum import Enum

import salabim as sim

from model import Utilities, GlobalVars
from model.Node import Node


class CrossRoadType(Enum):
    AdvanceRight = 1
    CyclicSigns = 2
    SmartSigns = 3


class CrossRoad(Node, sim.Component):
    def __init__(self, coordinates_pair):
        super().__init__(coordinates_pair[0], coordinates_pair[1])
        self.intersections = {}
        self.intersections_list = None
        self.claim = sim.Resource()
        self.crossroad_empty = True
        self.last_queue_tmp = None

    def draw(self):
        coordinate_tuple = Utilities.normalize(self.x, self.y)
        size = 2
        if GlobalVars.zoom:
            size = size / 2
        self.animate = sim.AnimatePoints(spec=coordinate_tuple, linecolor='red', linewidth=size, layer=3)

    def init_node(self, graph):
        if self.useful:
            self.last_queue_tmp = list(self.intersections.values())[-1]
            self.intersections_list = list(self.intersections.values())
            sim.Component.__init__(self)

    def process(self):
        if GlobalVars.crossroad_type == CrossRoadType.AdvanceRight:
            while True:
                queue = self.find_most_right_filled_queue()
                if queue is None:
                    self.crossroad_empty = True
                    yield self.passivate()
                else:
                    self.crossroad_empty = False
                    vessel = queue.pop(0)
                    vessel.activate()
                    yield self.passivate()
        elif GlobalVars.crossroad_type == CrossRoadType.CyclicSigns:
            index = 0
            queues = self.intersections_list
            queues_count = len(queues)
            previous_switch = GlobalVars.environment.now()
            while True:
                queue = queues[index]
                if len(queue) > 0:
                    vessel = queue.pop()
                    vessel.activate()
                yield self.hold(GlobalVars.crossroad_cyclic_inter_vessel_delay)
                if previous_switch + GlobalVars.crossroad_cyclic_delay <= GlobalVars.environment.now():
                    index += 1
                    index = index % queues_count
                    previous_switch = GlobalVars.environment.now()
                    yield self.hold(GlobalVars.crossroad_cyclic_clear_time)
        elif GlobalVars.crossroad_type == CrossRoadType.SmartSigns:
            index = 0
            queues = self.intersections_list
            queues_count = len(queues)
            previous_switch = GlobalVars.environment.now()
            while True:
                queue = queues[index]
                if len(queue) > 0:
                    vessel = queue.pop()
                    vessel.activate()
                yield self.hold(GlobalVars.crossroad_cyclic_inter_vessel_delay)
                if previous_switch + GlobalVars.crossroad_cyclic_delay <= GlobalVars.environment.now() or len(
                        queue) == 0:
                    next_index = self.find_next_index_filled_queue(index)
                    if next_index == -1:
                        self.passivate()
                    else:
                        if next_index == index:
                            previous_switch = GlobalVars.environment.now()
                        else:
                            index = next_index
                            previous_switch = GlobalVars.environment.now()
                            yield self.hold(GlobalVars.crossroad_cyclic_clear_time)

    def find_most_right_filled_queue(self):
        last_queue = self.last_queue_tmp
        for queue in self.intersections_list:
            if len(queue) == 0 and len(last_queue) != 0:
                return last_queue
            last_queue = queue
        if len(last_queue) == 0:
            return None
        else:
            return last_queue

    def find_next_index_filled_queue(self, index):
        queues = self.intersections_list
        queues_count = len(queues)
        current_index = index + 1
        current_index = current_index % queues_count
        while current_index != index:
            if len(queues[current_index]) != 0:
                return current_index
            current_index += 1
            current_index = current_index % queues_count
        if len(queues[index]) != 0:
            return index
        return -1
