import networkx as nx
import salabim as sim
import math

from model import GlobalVars, Utilities

left = -1
right = +1


class Vessel(object):
    speed = 9 * 1000 / 60  # m/min

    def __init__(self, ship_id, length, width, cemt):
        self.id = ship_id
        if math.isnan(length):
            self.length = 1
        else:
            self.length = length
        if math.isnan(width):
            self.width = 1
        else:
            self.width = width
        self.cemt = cemt
        self.trajectory_route = []
        self.current_trajectory = None


class VesselComponent(sim.Component):

    def __init__(self, vessel, **kwargs):
        super().__init__(**kwargs)
        self.vessel = vessel
        self.animation = None
        self.pos = object
        self.nodes_path = []
        self.current_node = None
        self.next_node = None

    def process(self):
        while len(self.vessel.trajectory_route) != 0:
            self.vessel.current_trajectory = self.vessel.trajectory_route.pop()
            if len(self.nodes_path) != 0:
                self.nodes_path.pop()
            self.nodes_path.extend(
                GlobalVars.network.fairway_sections_dict[self.vessel.current_trajectory.section_ref].nodes)

        self.current_node = self.nodes_path.pop()
        while len(self.nodes_path) != 0:
            self.next_node = self.nodes_path.pop()
            ### CHECK IF CROSSROAD
            ### THE REAL STUFF
            yield self.perform_animation()
            ### STUFF
            if type(self.next_node).__name__ == 'Lock':
                yield from self.perform_lock()
            elif type(self.next_node).__name__ == 'Bridge':
                yield from self.perform_bridge()
            self.current_node = self.next_node
        if self.animation is not None:
            self.animation.remove()

    def perform_animation(self):
        if self.animation is not None:
            self.animation.remove()
        if self.vessel.current_trajectory is not None:
            start = (self.current_node.x, self.current_node.y)
            end = (self.next_node.x, self.next_node.y)
            if GlobalVars.network.graph.has_edge(start, end):
                edge = GlobalVars.network.graph.edges[start, end, 0]
                required_time = edge['length'] / self.vessel.speed
                start_xy = Utilities.normalize(*start)
                end_xy = Utilities.normalize(*end)
                self.animation = sim.Animate(circle0=(1 / 2,), fillcolor0="black", x0=start_xy[0],
                                             x1=end_xy[0],
                                             y0=start_xy[1], y1=end_xy[1],
                                             t1=GlobalVars.environment.now() + required_time)

                return self.hold(required_time)
            else:
                return self.hold(0)

    def perform_lock(self):
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
        yield self.hold(lock.in_time)
        self.release(lock.key_in[side])
        yield self.request(lock.key_out)
        yield self.hold(lock.out_time)
        # self.leave(lockqueue)
        self.release(lock.key_out)

    def perform_bridge(self):
        bridge = self.next_node

        if bridge.ispassive():
            bridge.activate()

        yield self.request(bridge.key_in)
        bridge.hold(10 + bridge.pass_time)
        yield self.hold(bridge.pass_time)
        self.release(bridge.key_in)


class VesselComponentGenerator(sim.Component):
    def process(self):
        for _, vessel in GlobalVars.vessels_dict.items():
            VesselComponent(vessel)
            yield self.hold(sim.Poisson(10).sample())
