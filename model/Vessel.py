class Vessel(object):
    def __init__(self, ship_id, length, width, cemt):
        self.id = ship_id
        self.length = length
        self.width = width
        self.cemt = cemt
        self.trajectory_route = []
