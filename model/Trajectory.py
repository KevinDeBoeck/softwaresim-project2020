class Trajectory(object):
    """Defines a trajectory, having four coordinates"""

    def __init__(self, lon1, lat1):
        self.lon1 = lon1
        self.lat1 = lat1
        self.lon2 = None
        self.lat2 = None
