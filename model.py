# Read the passages
class Vessel(object):
    def __init__(self, shipID, length, width, cemt):
        self.id = shipID
        self.length = length
        self.width = width
        self.cemt = cemt
        self.route = []


class Trajectory(object):
    """Defines a trajectory, having four coordinates"""

    def __init__(self, lon1, lat1):
        self.lon1 = lon1
        self.lat1 = lat1
