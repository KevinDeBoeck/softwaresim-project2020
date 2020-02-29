class Bridge(object):
    """Defines a bridge"""

    def __init__(self, name, type, height_open, height_closed, width_single, width_combined, geometry):
        self.geometry = geometry
        self.width_combined = width_combined
        self.width_single = width_single
        self.height_closed = height_closed
        self.height_open = height_open
        self.type = type
        self.name = name

    def animate(self):
        print()