import math
import random

import salabim as sim

from model import GlobalVars, Utilities
from model.CrossRoad import CrossRoadType

left = -1
right = +1

closed = -1
open = +1

DOWN = -1
UP = +1


class Vessel(object):

    def __init__(self, ship_id, length, width, height, cemt):
        self.id = ship_id
        if math.isnan(length) or length == 0:
            self.length = 1
        else:
            self.length = length
        if math.isnan(width) or width == 0:
            self.width = 1
        else:
            self.width = width
        if math.isnan(height) or height == 0:
            self.height = 1
        else:
            self.height = height
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
        self.previous_node = None
        self.current_node = None
        self.next_node = None
        self.next_special_node = None
        self.stop_time = float('inf')
        self.remaining_time = 0
        self.trajectories = []
        tmp = self.vessel.trajectory_route.copy()
        if len(tmp) == 1:
            self.trajectories.append((tmp[0], UP))
        elif len(tmp) >= 2:
            first = tmp.pop(0)
            second = tmp.pop(0)
            if first.get_start_point(UP) == second.get_start_point(UP):
                self.trajectories.append((first, DOWN))
                self.trajectories.append((second, UP))
            elif first.get_end_point(UP) == second.get_start_point(UP):
                self.trajectories.append((first, UP))
                self.trajectories.append((second, UP))
            elif first.get_start_point(UP) == second.get_end_point(UP):
                self.trajectories.append((first, DOWN))
                self.trajectories.append((second, DOWN))
            elif first.get_end_point(UP) == second.get_end_point(UP):
                self.trajectories.append((first, UP))
                self.trajectories.append((second, DOWN))
            count = 1
            while len(tmp) != 0:
                route = tmp.pop(0)
                if self.trajectories[count][0].get_end_point(self.trajectories[count][1]) == route.get_start_point(
                        UP):
                    self.trajectories.append((route, UP))
                else:
                    self.trajectories.append((route, DOWN))
                count += 1

    def process(self):
        self.enter(GlobalVars.queue_vessels_in_network)
        GlobalVars.update_counters()

        for trajectory, direction in self.trajectories:
            if len(self.nodes_path) != 0:
                self.nodes_path.pop()
            if direction == UP:
                self.nodes_path.extend(trajectory.nodes)
            else:
                self.nodes_path.extend(reversed(trajectory.nodes))

        # for section_ref in range(15102, 15107):
        #     if len(self.nodes_path) != 0:
        #         self.nodes_path.pop()
        #     self.nodes_path.extend(
        #         GlobalVars.network.fairway_sections_dict[str(section_ref)].nodes)

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
        if len(self.special_nodes_path) != 0 and self.current_node == self.next_special_node:
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

            if type(self.next_node).__name__ == 'Lock':
                yield from self.perform_lock()
            elif type(self.next_node).__name__ == 'Bridge':
                yield from self.perform_bridge()
            self.previous_node = self.current_node
            self.current_node = self.next_node
            yield from self.check_new_fairway()
        if self.animation is not None:
            self.animation.remove()

        self.leave(GlobalVars.queue_vessels_in_network)
        GlobalVars.num_vessels_finished = GlobalVars.num_vessels_finished + 1
        GlobalVars.update_counters()
        print("Vessel " + str(self.vessel.id) + " finished at " + str(GlobalVars.environment.now()))

    def perform_animation(self):
        start = (self.current_node.x, self.current_node.y)
        end = (self.next_node.x, self.next_node.y)
        size = 1
        if GlobalVars.network.graph.has_edge(start, end):
            edge = GlobalVars.network.graph.edges[start, end, 0]
            required_time = edge['time']
            start_xy = Utilities.normalize(*start)
            end_xy = Utilities.normalize(*end)
            if self.animation is None:
                self.animation = sim.Animate(circle0=(size,), fillcolor0="black", x0=start_xy[0],
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
            self.previous_node = self.current_node
            self.current_node = self.next_node
            yield from self.check_new_fairway(doing_crossroad=True)
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
        self.enter(GlobalVars.queue_vessels_waiting_lock)
        GlobalVars.update_counters()

        lock = self.next_node
        if lock.left == (self.current_node.x, self.current_node.y):
            side = left
        else:
            side = right

        if lock.ispassive():
            lock.activate()
        possible = False
        resized = False

        self.enter(lock.wait_in[side])
        while not possible:
            if lock.side == side:
                if not lock.check_fit_empty(self.vessel):
                    resized = True
                    old_length = self.vessel.length
                    old_width = self.vessel.width
                    if self.vessel.length > lock.length:
                        self.vessel.length = lock.length
                    if self.vessel.width > lock.width:
                        self.vessel.width = lock.width
                if lock.check_fit(self.vessel):
                    possible = True
                    continue
            yield self.passivate()
        self.leave(lock.wait_in[side])

        yield self.request(lock.key_in[side])
        if lock.waiting:
            lock.hold(GlobalVars.lock_wait_time + GlobalVars.lock_inout_time)
        yield self.hold(GlobalVars.lock_inout_time)
        self.release(lock.key_in[side])

        if len(lock.wait_in[side]) > 0:
            lock.wait_in[side][0].activate()

        yield self.request(lock.key_out)
        yield self.hold(GlobalVars.lock_inout_time)
        self.release(lock.key_out)

        if len(self.special_nodes_path) != 0:
            self.next_special_node = self.special_nodes_path.pop(0)
        else:
            self.next_special_node = None
        self.stop_time = float('inf')

        self.leave(GlobalVars.queue_vessels_waiting_lock)

        if resized:
            self.vessel.length = old_length
            self.vessel.width = old_width
        # print(','.join(vessel.vessel.id for vessel in GlobalVars.queue_vessels_waiting_lock))
        GlobalVars.update_counters()

    def perform_bridge(self):
        bridge = self.next_node

        yield self.request(bridge.order)

        if bridge.check_fit_closed(self):
            yield self.request(bridge.moving)
            yield self.hold(GlobalVars.bridge_pass_time)
            self.release(bridge.moving)
        else:
            self.enter(GlobalVars.queue_vessels_waiting_bridge)
            GlobalVars.update_counters()

            yield self.request(bridge.moving)

            if bridge.state == open:
                bridge.hold(GlobalVars.bridge_min_wait + GlobalVars.bridge_pass_time)
                yield self.hold(GlobalVars.bridge_pass_time)
                self.leave(GlobalVars.queue_vessels_waiting_bridge)
                self.release(bridge.moving)
                GlobalVars.update_counters()
            else:
                if bridge.ispassive():
                    bridge.activate()
                self.release(bridge.moving)
                yield self.hold(0)
                yield self.request(bridge.moving)
                bridge.hold(GlobalVars.bridge_min_wait + GlobalVars.bridge_pass_time)
                yield self.hold(GlobalVars.bridge_pass_time)
                self.leave(GlobalVars.queue_vessels_waiting_bridge)
                self.release(bridge.moving)
                GlobalVars.update_counters()
        self.release(bridge.order)
        if bridge.movable:
            if len(self.special_nodes_path) != 0:
                self.next_special_node = self.special_nodes_path.pop(0)
            else:
                self.next_special_node = None
            self.stop_time = float('inf')

    def perform_crossroad(self):
        self.enter(GlobalVars.queue_vessels_waiting_crossroad)
        GlobalVars.update_counters()

        # print("ENTERED: " + str(self.vessel.id))
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

        self.leave(GlobalVars.queue_vessels_waiting_crossroad)
        GlobalVars.update_counters()

        yield from self.check_new_fairway_after_crossroad()

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
        return float('inf')
        # print("WE DID NOT ENCOUNTER THE SPECIAL NODE: %s" % self.vessel.id)

    def get_node_before_crossroad(self):
        previous = (self.nodes_path[0].x, self.nodes_path[0].y)
        for node in self.nodes_path:
            if node is self.next_special_node:
                return previous.x, previous.y
            else:
                previous = node

    def check_new_fairway(self, doing_crossroad=False):
        current_trajectory = self.trajectories[0][0]
        current_direction = self.trajectories[0][1]
        if self.current_node == current_trajectory.get_end_point(current_direction):
            self.trajectories.pop(0)
            current_trajectory.moving[current_direction].remove(self)
            for vessel in current_trajectory.waiting[-current_direction]:
                vessel.activate()
        else:
            if self.previous_node == current_trajectory.get_start_point(current_direction):
                current_trajectory.waiting[current_direction].append(self)
                self.enter(GlobalVars.queue_vessels_waiting_segment)
                GlobalVars.update_counters()
                while not doing_crossroad and not self.can_enter():
                    yield self.passivate()
                self.leave(GlobalVars.queue_vessels_waiting_segment)
                GlobalVars.update_counters()
                current_trajectory.waiting[current_direction].remove(self)
                current_trajectory.moving[current_direction].append(self)

    def check_new_fairway_after_crossroad(self):
        current_trajectory = self.trajectories[0][0]
        current_direction = self.trajectories[0][1]
        current_trajectory.moving[current_direction].remove(self)
        current_trajectory.waiting[current_direction].append(self)
        self.enter(GlobalVars.queue_vessels_waiting_segment)
        GlobalVars.update_counters()
        while not self.can_enter():
            yield self.passivate()
        self.leave(GlobalVars.queue_vessels_waiting_segment)
        GlobalVars.update_counters()
        current_trajectory.waiting[current_direction].remove(self)
        current_trajectory.moving[current_direction].append(self)

    def can_enter(self):
        current_trajectory = self.trajectories[0][0]
        current_direction = self.trajectories[0][1]
        for vessel in current_trajectory.moving[-current_direction]:
            if not current_trajectory.cross_table[self.vessel.cemt][vessel.vessel.cemt]:
                return False
        return True


class VesselComponentGenerator(sim.Component):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.distr = sim.Bounded(sim.Exponential(30.9012), upperbound=200)

    def process(self):
        vessels = list(GlobalVars.vessels_dict.values())

        while len(vessels) > 0:
            vessel = random.choice(vessels)
            vessels.remove(vessel)
            # for vessel in vessels:
            VesselComponent(vessel)
            yield self.hold(self.distr.sample())
