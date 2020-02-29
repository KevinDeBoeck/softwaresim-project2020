import salabim as sim
import simulation
import math
import numpy as np


class Vessel(sim.Component, sim.Animate):
    speed = 9  # km/h

    def __init__(self, shipID, length, width, cemt):
        self.id = shipID
        self.length = length
        self.width = width
        self.cemt = cemt
        self.route = []
        self.current_trajectory = None


class VesselComponent(sim.Component, sim.Animate):

    def __init__(self, vessel, **kwargs):
        super().__init__(**kwargs)
        self.vessel = vessel
        self.animation = None
        self.pos = object

    def process(self):
        while len(self.vessel.route) != 0:
            yield self.perform_animation()
        self.animation.remove()

    def perform_animation(self):
        draw_scale = simulation.draw_scale
        if self.animation is not None:
            self.animation.remove()
        self.vessel.current_trajectory = self.vessel.route.pop()
        if self.vessel.current_trajectory is not None:
            start_xy = (self.vessel.current_trajectory.lon1, self.vessel.current_trajectory.lat1)
            end_xy = (self.vessel.current_trajectory.lon2, self.vessel.current_trajectory.lat2)
            distance = haversine_np(self.vessel.current_trajectory.lon1, self.vessel.current_trajectory.lat1,
                                    self.vessel.current_trajectory.lon2, self.vessel.current_trajectory.lat2)
            required_time = distance / Vessel.speed * 60  # Time in minutes

            self.animation = sim.Animate(circle0=(0.005,), fillcolor0="black", x0=start_xy[0] * draw_scale,
                                         x1=end_xy[0] * draw_scale,
                                         y0=start_xy[1] * draw_scale, y1=end_xy[1] * draw_scale,
                                         t0=simulation.environment.now(),
                                         t1=simulation.environment.now() + required_time)

            return self.hold(required_time)


class VesselComponentGenerator(sim.Component):
    def process(self):
        for id, vessel in simulation.vessels_dict.items():
            VesselComponent(vessel)
            yield self.hold(sim.Poisson(10).sample())


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km
