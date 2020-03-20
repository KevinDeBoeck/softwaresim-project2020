import cmath
import math

# import matplotlib.pyplot as plt
import networkx as nx
import salabim as sim

from model import GlobalVars, Utilities
from model.CrossRoad import CrossRoad


def angle_between_points(point_a_pair, point_b_pair):
    x = point_b_pair[0] - point_a_pair[0]
    y = point_b_pair[1] - point_a_pair[1]
    z = complex(x, y)
    angle = cmath.phase(z)
    if angle < 0:
        angle = angle + 2 * math.pi
    return angle / math.pi * 180


class Network:

    def __init__(self):
        self.graph = nx.MultiGraph()
        self.fairway_sections_list = GlobalVars.fairway_section_list
        self.fairway_sections_dict = GlobalVars.fairway_section_dict

        for bridge in GlobalVars.bridges:
            self.fairway_sections_dict[bridge.fw_code].bridges.append(bridge)

        for lock in GlobalVars.locks:
            self.fairway_sections_dict[lock.fw_code].locks.append(lock)

    def draw_network(self):
        for fairway in self.fairway_sections_list:
            fairway.draw()

    def generate_graph(self):
        """LETS SCREAM IT OUT"""
        stop = (3.4084978395216, 50.911124847130168)
        for fairway in self.fairway_sections_list:
            start_pair = None
            for node in fairway.nodes:
                end_pair = (node.x, node.y)
                if end_pair == stop:
                    print("STOP")

                if type(node).__name__ == 'Node':
                    if not self.graph.has_node(end_pair):
                        self.graph.add_node(end_pair, artwork=None, pos=end_pair, fairway=fairway)
                else:
                    if not self.graph.has_node(end_pair):
                        self.graph.add_node(end_pair, artwork=node, pos=end_pair, fairway=fairway)
                    else:
                        self.graph.nodes()[end_pair]['artwork'] = node
                if start_pair is not None:
                    self.graph.add_edge(start_pair, end_pair, fairway=fairway,
                                        length=Utilities.haversine(start_pair, end_pair))
                start_pair = end_pair

        stop = (3.4084978395216, 50.911124847130168)
        for node in self.graph.nodes:
            neighbors = list(self.graph.neighbors(node))
            if node == stop:
                print("STOP")
            if len(neighbors) > 2:
                crossroad = CrossRoad(node)
                crossroad.draw()
                self.graph.nodes()[node]['artwork'] = crossroad
                neighbors = sorted(neighbors, key=lambda element: angle_between_points(node, element))
                for neighbor in neighbors:
                    crossroad.intersections[neighbor] = sim.Queue(
                        "Crosroad: " + str(node) + " => " + str(neighbor))

        # nx.draw(self.graph, pos=nx.get_node_attributes(self.graph, 'pos'), node_size=1, alpha=0.5, node_color="blue",
        #         with_labels=False)
        # plt.axis('scaled')
        # plt.show()
