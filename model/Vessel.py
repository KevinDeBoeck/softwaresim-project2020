import math

import salabim as sim

from model import GlobalVars, Utilities
from model.CrossRoad import CrossRoadType

left = -1
right = +1


class Vessel(object):

    def __init__(self, ship_id, length, width, cemt):
        self.id = ship_id
        if math.isnan(length) or length == 0:
            self.length = 1
        else:
            self.length = length
        if math.isnan(width) or width == 0:
            self.width = 1
        else:
            self.width = width
        self.cemt = cemt
        self.trajectory_route = []


class VesselComponent(sim.Component):

    def __init__(self, vessel, **kwargs):
        super().__init__(**kwargs)
        self.vessel = vessel
        self.animation = None
        self.pos = object
        self.nodes_path = []
        self.special_nodes_path = []
        self.current_node = None
        self.next_node = None
        self.next_special_node = None
        self.stop_time = float('inf')
        self.remaining_time = 0

    def process(self):
        GlobalVars.num_vessels_in_network = GlobalVars.num_vessels_in_network + 1
        GlobalVars.update_counters()
        """
        while len(self.vessel.trajectory_route) != 0:
            self.vessel.current_trajectory = self.vessel.trajectory_route.pop(0)
            if len(self.nodes_path) != 0:
                self.nodes_path.pop()
            self.nodes_path.extend(
                GlobalVars.network.fairway_sections_dict[self.vessel.current_trajectory.section_ref].nodes)
        """

        for section_ref in range(15102, 15107):
            if len(self.nodes_path) != 0:
                self.nodes_path.pop()
            self.nodes_path.extend(
                GlobalVars.network.fairway_sections_dict[str(section_ref)].nodes)

        for idx, node in enumerate(self.nodes_path):
            node_pos = (node.x, node.y)
            artwork = GlobalVars.network.graph.nodes()[node_pos]['artwork']
            if (artwork.x, artwork.y) == (node.x, node.y):
                self.nodes_path[idx] = artwork
            if type(artwork).__name__ != 'Node':
                if type(artwork).__name__ != 'Bridge' or artwork.movable is True:
                    self.special_nodes_path.append(GlobalVars.network.graph.nodes()[node_pos]['artwork'])

        self.current_node = self.nodes_path.pop(0)
        if len(self.special_nodes_path) != 0:
            self.next_special_node = self.special_nodes_path.pop(0)
        while len(self.nodes_path) != 0:
            if type(self.next_special_node).__name__ == 'CrossRoad':
                if self.stop_time == float('inf'):
                    self.stop_time = self.time_till_next_special_node()
                    self.stop_time = self.stop_time - GlobalVars.crossroad_stop_time
                    if self.stop_time < 0:
                        self.stop_time = 0

            self.next_node = self.nodes_path.pop(0)

            yield from self.perform_animation()

            # PERFORM CROSSROAD
            if self.stop_time == 0:
                yield from self.perform_crossroad()

            ### CHECK IF CROSSROAD
            ### THE REAL STUFF
            ### STUFF
            if type(self.next_node).__name__ == 'Lock':
                yield from self.perform_lock()
            elif type(self.next_node).__name__ == 'Bridge':
                yield from self.perform_bridge()
            self.current_node = self.next_node
        if self.animation is not None:
            self.animation.remove()

        GlobalVars.num_vessels_in_network = GlobalVars.num_vessels_in_network - 1
        GlobalVars.num_vessels_finished = GlobalVars.num_vessels_finished + 1
        GlobalVars.update_counters()
        print("Vessel " + str(self.vessel.id) + " finished at " + str(GlobalVars.environment.now()))

    def perform_animation(self):
        start = (self.current_node.x, self.current_node.y)
        end = (self.next_node.x, self.next_node.y)
        if GlobalVars.network.graph.has_edge(start, end):
            edge = GlobalVars.network.graph.edges[start, end, 0]
            required_time = edge['time']
            start_xy = Utilities.normalize(*start)
            end_xy = Utilities.normalize(*end)
            if self.animation is None:
                self.animation = sim.Animate(circle0=(1 / 2,), fillcolor0="black", x0=start_xy[0],
                                             x1=end_xy[0],
                                             y0=start_xy[1], y1=end_xy[1],
                                             t1=GlobalVars.environment.now() + required_time, layer=1)
            else:
                self.animation.update(x1=end_xy[0], y1=end_xy[1],
                                      t1=GlobalVars.environment.now() + required_time)

            if required_time <= self.stop_time:
                yield self.hold(required_time)
                self.stop_time -= required_time
            else:
                yield self.hold(self.stop_time)
                self.remaining_time = required_time - self.stop_time
                self.stop_time = 0
                self.animation.update(x1=self.animation.x(), y1=self.animation.y())
        else:
            yield self.hold(0)

    def perform_animation_to_crossroad(self):
        # MOVE TO END OF NODE
        start = (self.current_node.x, self.current_node.y)
        end = (self.next_node.x, self.next_node.y)
        if GlobalVars.network.graph.has_edge(start, end):
            edge = GlobalVars.network.graph.edges[start, end, 0]
            required_time = self.remaining_time
            end_xy = Utilities.normalize(*end)
            self.animation.update(x1=end_xy[0], y1=end_xy[1],
                                  t1=GlobalVars.environment.now() + required_time)

            yield self.hold(required_time)
        self.remaining_time = 0

        # FINISH REMAINING NODES TILL CROSSROAD
        while self.next_node != self.next_special_node:
            self.current_node = self.next_node
            self.next_node = self.nodes_path.pop(0)
            start = (self.current_node.x, self.current_node.y)
            end = (self.next_node.x, self.next_node.y)
            if GlobalVars.network.graph.has_edge(start, end):
                edge = GlobalVars.network.graph.edges[start, end, 0]
                required_time = edge['time']
                end_xy = Utilities.normalize(*end)
                self.animation.update(x1=end_xy[0], y1=end_xy[1],
                                      t1=GlobalVars.environment.now() + required_time)

                yield self.hold(required_time)

    def perform_lock(self):
        GlobalVars.num_vessels_waiting_lock = GlobalVars.num_vessels_waiting_lock + 1
        GlobalVars.update_counters()

        lock = self.next_node
        if lock.left == (self.current_node.x, self.current_node.y):
            side = left
        else:
            side = right

        if lock.ispassive():
            lock.activate()
        possible = False
        while not possible:
            if lock.side == side:
                if lock.check_fit(self.vessel):
                    possible = True
                    continue
            self.enter(lock.wait_in[side])
            yield self.passivate()
            self.leave(lock.wait_in[side])
        yield self.request(lock.key_in[side])
        # self.enter(lockqueue)
        yield self.hold(GlobalVars.lock_inout_time)
        self.release(lock.key_in[side])
        yield self.request(lock.key_out)
        yield self.hold(GlobalVars.lock_inout_time)
        # self.leave(lockqueue)
        self.release(lock.key_out)

        if len(self.special_nodes_path) != 0:
            self.next_special_node = self.special_nodes_path.pop(0)
        else:
            self.next_special_node = None
        self.stop_time = float('inf')

        GlobalVars.num_vessels_waiting_lock = GlobalVars.num_vessels_waiting_lock - 1
        GlobalVars.update_counters()

    def perform_bridge(self):
        bridge = self.next_node
        if bridge.movable:
            GlobalVars.num_vessels_waiting_bridge = GlobalVars.num_vessels_waiting_bridge + 1
            GlobalVars.update_counters()

            if bridge.ispassive():
                bridge.activate()

            yield self.request(bridge.key_in)

            bridge.hold(10 + GlobalVars.bridge_pass_time)
            yield self.hold(GlobalVars.bridge_pass_time)
            if len(self.special_nodes_path) != 0:
                self.next_special_node = self.special_nodes_path.pop(0)
            else:
                self.next_special_node = None
            self.stop_time = float('inf')
            self.release(bridge.key_in)

            GlobalVars.num_vessels_waiting_bridge = GlobalVars.num_vessels_waiting_bridge - 1
            GlobalVars.update_counters()

    def perform_crossroad(self):
        GlobalVars.num_vessels_waiting_crossroad = GlobalVars.num_vessels_waiting_crossroad + 1
        GlobalVars.update_counters()

        # print("ENTERED: " + self.vessel.id)
        crossroad = self.next_special_node

        if GlobalVars.crossroad_type == CrossRoadType.AdvanceRight:
            self.enter(crossroad.intersections[self.get_node_before_crossroad()])
            if crossroad.ispassive() and crossroad.crossroad_empty:
                crossroad.activate()
            yield self.passivate()
            yield self.request(crossroad.claim)
            yield from self.perform_animation_to_crossroad()
            self.release(crossroad.claim)
            if crossroad.ispassive():
                crossroad.activate()
        elif GlobalVars.crossroad_type == CrossRoadType.CyclicSigns:
            self.enter(crossroad.intersections[self.get_node_before_crossroad()])
            yield self.passivate()
            yield from self.perform_animation_to_crossroad()
        elif GlobalVars.crossroad_type == CrossRoadType.SmartSigns:
            self.enter(crossroad.intersections[self.get_node_before_crossroad()])
            if crossroad.ispassive():
                crossroad.activate()
            yield self.passivate()
            yield from self.perform_animation_to_crossroad()

        if len(self.special_nodes_path) != 0:
            self.next_special_node = self.special_nodes_path.pop(0)
        else:
            self.next_special_node = None
        self.stop_time = float('inf')
        # print("LEFT: " + self.vessel.id)

        GlobalVars.num_vessels_waiting_crossroad = GlobalVars.num_vessels_waiting_crossroad - 1
        GlobalVars.update_counters()

    def time_till_next_special_node(self):
        start = (self.current_node.x, self.current_node.y)
        time = 0
        for node in self.nodes_path:
            end = (node.x, node.y)
            if not GlobalVars.network.graph.has_edge(start, end):
                time += 0
            else:
                edge = GlobalVars.network.graph.edges[start, end, 0]
                time += edge['time']
            start = end
            if node == self.next_special_node:
                return time
        print("WE DID NOT ENCOUNTER THE SPECIAL NODE")

    def get_node_before_crossroad(self):
        for node in self.nodes_path:
            if node is self.next_special_node:
                return previous.x, previous.y
            else:
                previous = node


class VesselComponentGenerator(sim.Component):
    def process(self):
        for _, vessel in GlobalVars.vessels_dict.items():
            VesselComponent(vessel)
            yield self.hold(sim.Poisson(10).sample())
