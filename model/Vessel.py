import salabim as sim

from model import GlobalVars, Utilities


class Vessel(object):
    speed = 9

    def __init__(self, ship_id, length, width, cemt):
        self.id = ship_id
        self.length = length
        self.width = width
        self.cemt = cemt
        self.trajectory_route = []
        self.current_trajectory = None


class VesselComponent(sim.Component):

    def __init__(self, vessel, **kwargs):
        super().__init__(**kwargs)
        self.vessel = vessel
        self.animation = None
        self.pos = object

    def process(self):
        while len(self.vessel.trajectory_route) != 0:
            yield self.perform_animation()
        self.animation.remove()

    def perform_animation(self):
        if self.animation is not None:
            self.animation.remove()
        self.vessel.current_trajectory = self.vessel.trajectory_route.pop()
        if self.vessel.current_trajectory is not None:
            start_xy = (self.vessel.current_trajectory.lon1, self.vessel.current_trajectory.lat1)
            end_xy = (self.vessel.current_trajectory.lon2, self.vessel.current_trajectory.lat2)
            distance = Utilities.haversine(start_xy, end_xy) / 1000  # Distance in meters
            required_time = distance / Vessel.speed * 60  # Time in minutes

            start_xy = Utilities.normalize(start_xy[0], start_xy[1])
            end_xy = Utilities.normalize(end_xy[0], end_xy[1])
            self.animation = sim.Animate(circle0=(1/2,), fillcolor0="black", x0=start_xy[0],
                                         x1=end_xy[0],
                                         y0=start_xy[1], y1=end_xy[1],
                                         t1=GlobalVars.environment.now() + required_time)

            return self.hold(required_time)


class VesselComponentGenerator(sim.Component):
    def process(self):
        for _, vessel in GlobalVars.vessels_dict.items():
            VesselComponent(vessel)
            yield self.hold(sim.Poisson(10).sample())
