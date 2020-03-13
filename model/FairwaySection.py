class FairwaySection(object):
    """Defines a waterway"""

    def __init__(self, properties, lon1, lat1, lon2, lat2, geometry):
        self.properties = properties
        self.bridges = []
        self.terminals = []
        self.locks = []
        self.lon1 = lon1
        self.lat1 = lat1
        self.lon2 = lon2
        self.lat2 = lat2
        self.geometry = geometry

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def add_terminal(self, terminal):
        self.terminals.append(terminal)

    def add_lock(self, lock):
        self.locks.append(lock)
