import networkx as nx
import salabim as sim
from shapely.geometry import LineString
from shapely.geometry import Point

import simulation


def dist_trajectory_from_fairway(fairway, trajectory):
    point_trajectory_a = Point(trajectory.lon1, trajectory.lat1)
    point_trajectory_b = Point(trajectory.lon2, trajectory.lat2)
    point_fairway_a = Point(fairway.lon1, fairway.lat1)
    point_fairway_b = Point(fairway.lon2, fairway.lat2)
    dist = point_fairway_a.distance(point_trajectory_a) + point_fairway_a.distance(
        point_trajectory_b) + point_fairway_b.distance(point_trajectory_a) + point_fairway_b.distance(
        point_trajectory_b)
    return dist


def project_trajectory_on_fairway(fairway, trajectory):
    point_trajectory_a = Point(trajectory.lon1, trajectory.lat1)
    point_trajectory_b = Point(trajectory.lon2, trajectory.lat2)
    line = LineString([(fairway.lon1, fairway.lat1), (fairway.lon2, fairway.lat2)])
    dist = line.project(point_trajectory_a)
    projection = list(line.interpolate(dist).coords)
    trajectory.projected_lon1 = projection[0][0]
    trajectory.projected_lat1 = projection[0][1]
    dist = line.project(point_trajectory_b)
    projection = list(line.interpolate(dist).coords)
    trajectory.projected_lon2 = projection[0][0]
    trajectory.projected_lat2 = projection[0][1]


def project_point_on_fairway(fairway, artwork):
    point = Point(artwork.lon, artwork.lat)
    line = LineString([(fairway.lon1, fairway.lat1), (fairway.lon2, fairway.lat2)])
    dist = line.project(point)
    projection = list(line.interpolate(dist).coords)
    artwork.projected_lon = projection[0][0]
    artwork.projected_lat = projection[0][1]


class Network(object):

    def __init__(self):
        self.fairway_sections = {}
        self.trajectories = None
        self.graph = nx.MultiGraph()
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0

    def add_fairway_section(self, fw_code, section):
        self.fairway_sections[fw_code] = section

    def add_trajectory(self, trajectory):
        self.trajectories = trajectory

    def generate_network(self):
        """LETS SCREAM IT OUT"""

        print("Generating fairway sections graph")
        for index, fairway in self.fairway_sections.items():
            start = (fairway.lon1, fairway.lat1)
            end = (fairway.lon2, fairway.lat2)
            self.graph.add_edge(start, end, fairway=fairway)

        print("Mapping trajectories to fairway sections")
        for key_a, trajectory in self.trajectories.items():
            dist_from_fairways = {}
            lowest = 9000
            for _, fairway in self.fairway_sections.items():
                dist_from_fairways[dist_trajectory_from_fairway(fairway, trajectory)] = fairway
            for key_b in dist_from_fairways.keys():
                if key_b < lowest:
                    lowest = key_b
            trajectory.fairway_section = dist_from_fairways[lowest]
            dist_from_fairways.clear()
            print("Traject: " + key_a + "\tFairway: " + trajectory.fairway_section.properties[
                "fw_code"] + "\tDistance: " + str(lowest))

    def draw(self):
        """Draw the network"""
        env = simulation.environment
        self.setup_animation(env)
        draw_scale = simulation.draw_scale

        # Draw fairways
        print("Drawing fairway sections")
        for (_, _, fairway) in self.graph.edges.data('fairway'):
            if self.must_draw_line(fairway.lon1 * draw_scale, fairway.lat1 * draw_scale, fairway.lon2 * draw_scale,
                                   fairway.lat2 * draw_scale):
                sim.AnimateLine(
                    spec=(fairway.lon1 * draw_scale, fairway.lat1 * draw_scale, fairway.lon2 * draw_scale,
                          fairway.lat2 * draw_scale),
                    linewidth=0.005, linecolor="blue")

        # Draw bridges
        print("Drawing bridges")
        for (_, _, fairway) in self.graph.edges.data('fairway'):
            for bridge in fairway.bridges:
                project_point_on_fairway(fairway, bridge)
                if self.must_draw_point(bridge.projected_lon * draw_scale, bridge.projected_lat * draw_scale):
                    sim.AnimateCircle(radius=0.005, x=bridge.projected_lon * draw_scale,
                                      y=bridge.projected_lat * draw_scale,
                                      fillcolor="lime")

        # Draw terminals
        print("Drawing terminals")
        for (_, _, fairway) in self.graph.edges.data('fairway'):
            for terminal in fairway.terminals:
                project_point_on_fairway(fairway, terminal)
                if self.must_draw_point(terminal.projected_lon * draw_scale, terminal.projected_lat * draw_scale):
                    sim.AnimateCircle(radius=0.005, x=terminal.projected_lon * draw_scale,
                                      y=terminal.projected_lat * draw_scale,
                                      fillcolor="magenta")

        # Draw locks
        print("Drawing locks")
        for (_, _, fairway) in self.graph.edges.data('fairway'):
            for lock in fairway.locks:
                project_point_on_fairway(fairway, lock)
                if self.must_draw_point(lock.projected_lon * draw_scale, lock.projected_lat * draw_scale):
                    sim.AnimateCircle(radius=0.005, x=lock.projected_lon * draw_scale,
                                      y=lock.projected_lat * draw_scale,
                                      fillcolor="orangered")

        print("Drawing trajectories")
        for _, trajectory in self.trajectories.items():
            project_trajectory_on_fairway(trajectory.fairway_section,trajectory)
            if self.must_draw_line(trajectory.projected_lon1 * draw_scale, trajectory.projected_lat1 * draw_scale,
                                   trajectory.projected_lon2 * draw_scale,
                                   trajectory.projected_lat2 * draw_scale):
                sim.AnimateLine(
                    spec=(trajectory.projected_lon1 * draw_scale, trajectory.projected_lat1 * draw_scale,
                          trajectory.projected_lon2 * draw_scale,
                          trajectory.projected_lat2 * draw_scale),
                    linewidth=0.005, linecolor="red")

    def setup_animation(self, env):
        """ Setup draw dimensions"""
        print("Setting animation parameters")
        draw_scale = simulation.draw_scale

        self.x_min = 3.140237 * draw_scale
        self.y_min = 50.794897 * draw_scale
        self.x_max = 3.371636 * draw_scale
        self.y_max = self.y_min + (self.x_max - self.x_min)

        env.animation_parameters(x0=self.x_min, x1=self.x_max,
                                 y0=self.y_min, background_color="lightgray", height=simulation.height,
                                 width=simulation.width)

    def must_draw_line(self, x0, y0, x1, y1):
        if self.x_min < x0 < self.x_max and self.y_min < y0 < self.y_max:
            return True
        if self.x_min < x1 < self.x_max and self.y_min < y1 < self.y_max:
            return True
        return False

    def must_draw_point(self, x0, y0):
        if self.x_min < x0 < self.x_max and self.y_min < y0 < self.y_max:
            return True
        return False
