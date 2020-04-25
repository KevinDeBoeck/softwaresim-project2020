DOWN = -1
UP = +1


class Trajectory:
    """Defines a trajectory, having four coordinates"""

    def __init__(self, lon1, lat1, trajectory_name, section_ref_1):
        self.lon1 = lon1
        self.lat1 = lat1
        self.lon2 = None
        self.lat2 = None
        self.section_ref_1 = section_ref_1
        self.section_ref_2 = None
        self.trajectory_name = trajectory_name
        self.nodes = []
        self.cross_table = {}
        self.moving = {UP: [], DOWN: []}
        self.waiting = {UP: [], DOWN: []}

    def get_start_point(self, direction):
        if direction == UP:
            return self.nodes[0]
        else:
            return self.nodes[len(self.nodes) - 1]

    def get_end_point(self, direction):
        if direction == DOWN:
            return self.nodes[0]
        else:
            return self.nodes[len(self.nodes) - 1]
