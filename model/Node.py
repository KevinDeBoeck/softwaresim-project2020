from abc import ABC


class Node(ABC):
    """Defines a nodes of a trajectory"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animate = None
        self.useful = False

    def draw(self):
        pass

    def init_node(self, graph):
        pass
