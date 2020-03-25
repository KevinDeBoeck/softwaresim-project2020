class Trajectory:
    """Defines a trajectory, having four coordinates"""

    def __init__(self, lon1, lat1, trajectory_name, section_ref):
        self.lon1 = lon1
        self.lat1 = lat1
        self.trajectory_name = trajectory_name
        self.section_ref = section_ref
