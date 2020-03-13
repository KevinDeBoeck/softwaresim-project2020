class Trajectory(object):
    """Defines a trajectory, having four coordinates"""

    def __init__(self, lon1, lat1):
        self.lon1 = lon1
        self.lat1 = lat1
        self.lon2 = None
        self.lat2 = None
        self.fairway_section = None
        self.projected_lon1 = lon1
        self.projected_lat1 = lat1
        self.projected_lon2 = lon1
        self.projected_lat2 = lat1
