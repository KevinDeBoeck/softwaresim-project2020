from abc import ABC, abstractmethod


class Node(ABC):
    """Defines a nodes of a trajectory"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animate = None

    def draw(self):
        pass
