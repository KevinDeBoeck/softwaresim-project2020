import cmath
import math

import matplotlib.pyplot as plt
import networkx as nx
import salabim as sim
from shapely.geometry import LineString
from shapely.geometry import Point

import simulation
from model.CrossRoad import CrossRoad


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


def distance_artwork_from_point(point_a, artwork):
    point_b = Point(artwork.projected_lon, artwork.projected_lat)
    artwork.dist = point_b.distance(point_a)


def angle_between_points(point_a_pair, point_b_pair):
    x = point_b_pair[0] - point_a_pair[0]
    y = point_b_pair[1] - point_a_pair[1]
    z = complex(x, y)
    angle = cmath.phase(z)
    if angle < 0:
        angle = angle + 2 * math.pi
    return angle / math.pi * 180


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

    def generate_graph(self):
        """LETS SCREAM IT OUT"""

        count_map = {}

        print("Generating fairway sections graph")
        for index, fairway in self.fairway_sections.items():
            iterable_list = []
            iterable_list.extend(fairway.bridges)
            iterable_list.extend(fairway.locks)
            # iterable_list.extend(fairway.terminals)
            for artwork in iterable_list:
                distance_artwork_from_point(Point(fairway.lon1, fairway.lat1), artwork)
            iterable_list = sorted(iterable_list,
                                   key=lambda element: element.dist)

            start = Point(fairway.lon1, fairway.lat1)
            start_pair = (fairway.lon1, fairway.lat1)
            self.graph.add_node(start_pair, artwork=None, pos=(start_pair[0], start_pair[1]))
            if start_pair in count_map.keys():
                count_map[start_pair] = count_map[start_pair] + 1
            else:
                count_map[start_pair] = 1

            for artwork in iterable_list:
                end = Point(artwork.projected_lon, artwork.projected_lat)
                end_pair = (artwork.lon, artwork.lat)
                self.graph.add_node(end_pair, artwork=artwork, pos=(end_pair[0], end_pair[1]))
                self.graph.add_edge(start_pair, end_pair, fairway=fairway, length=start.distance(end))
                start = end
                start_pair = end_pair
            end = Point(fairway.lon2, fairway.lat2)
            end_pair = (fairway.lon2, fairway.lat2)
            self.graph.add_node(end_pair, artwork=None, pos=(end_pair[0], end_pair[1]))
            self.graph.add_edge(start_pair, end_pair, fairway=fairway, length=start.distance(end))
            if end_pair in count_map.keys():
                count_map[end_pair] = count_map[end_pair] + 1
            else:
                count_map[end_pair] = 1

        print("Num edges: " + str(len(self.graph.edges)))
        print("Num nodes: " + str(len(self.graph.nodes)))

        nodes = self.graph.nodes._nodes
        for point_pair, count in count_map.items():
            if count > 2:
                crossroad = CrossRoad(point_pair[0], point_pair[1])
                crossroad.draw()
                nodes[point_pair]['artwork'] = crossroad
                iterable_list_2 = []
                for neighbor in self.graph.neighbors(point_pair):
                    iterable_list_2.append(neighbor)

                iterable_list_2 = sorted(iterable_list_2, key=lambda element: angle_between_points(point_pair, element))
                for neighbor in iterable_list_2:
                    crossroad.intersections[neighbor] = sim.Queue(
                        "Crosroad: " + str(point_pair) + " => " + str(neighbor))

        nx.draw(self.graph, pos=nx.get_node_attributes(self.graph, 'pos'), node_size=1, alpha=0.5, node_color="blue",
                with_labels=False)
        plt.axis('scaled')
        plt.show()

    def draw_and_project(self):
        """Draw the network"""
        env = simulation.environment
        self.setup_animation(env)
        draw_scale = simulation.draw_scale

        # Draw fairways
        print("Drawing fairway sections")
        for _, fairway in self.fairway_sections.items():
            if self.must_draw_line(fairway.lon1 * draw_scale, fairway.lat1 * draw_scale, fairway.lon2 * draw_scale,
                                   fairway.lat2 * draw_scale):
                sim.AnimateLine(
                    spec=(fairway.lon1 * draw_scale, fairway.lat1 * draw_scale, fairway.lon2 * draw_scale,
                          fairway.lat2 * draw_scale),
                    linewidth=0.005, linecolor="blue")

        # Draw bridges
        print("Drawing bridges")
        for _, fairway in self.fairway_sections.items():
            for bridge in fairway.bridges:
                project_point_on_fairway(fairway, bridge)
                if self.must_draw_point(bridge.projected_lon * draw_scale, bridge.projected_lat * draw_scale):
                    bridge.draw()

        # Draw terminals
        print("Drawing terminals")
        for _, fairway in self.fairway_sections.items():
            for terminal in fairway.terminals:
                project_point_on_fairway(fairway, terminal)
                if self.must_draw_point(terminal.projected_lon * draw_scale, terminal.projected_lat * draw_scale):
                    terminal.draw()

        # Draw locks
        print("Drawing locks")
        for _, fairway in self.fairway_sections.items():
            for lock in fairway.locks:
                project_point_on_fairway(fairway, lock)
                if self.must_draw_point(lock.projected_lon * draw_scale, lock.projected_lat * draw_scale):
                    lock.draw()

    def setup_animation(self, env):
        """ Setup draw dimensions"""
        print("Setting animation parameters")
        draw_scale = simulation.draw_scale

        self.x_min = 3.140237 * draw_scale
        self.y_min = 50.794897 * draw_scale
        self.x_max = 3.371636 * draw_scale
        self.y_max = self.y_min + (self.x_max - self.x_min)

        env.animation_parameters(x0=self.x_min, x1=self.x_max,
                                 y0=self.y_min, background_color="lightgray")

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
