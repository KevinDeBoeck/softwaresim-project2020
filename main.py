# Read the different data files
import numpy as np
import salabim as sim

import IO
from model import Utilities, GlobalVars
from model.Network import Network

vessels_dict = {}
vessels = []


class Vessel(sim.Component):
    """Vessel Salabim component"""

    def process(self):
        # traverse a route (while loop)
        pass


class Vessel_generator(sim.Component):
    """Generate vessels with a given inter-arrival distribution"""

    def process(self):
        print(vessels_dict)
        print(vessels)

        print('test')


# Animate
def animate_simulation():
    """Animate the solution"""

    for fairway in GlobalVars.fairway_section_list:
        fairway_arr = np.array([[Utilities.normalize(node.x, node.y)] for node in fairway.nodes])

        # Make this a one-dimensional array (so we can generate a tuple easily)
        fairway_arr = fairway_arr.ravel()
        # Make a tuple (accepted by the 'AnimatePoints' function
        fairway_tuple = tuple(fairway_arr)
        # Draw all the fairway points on the map
        sim.AnimateLine(spec=fairway_tuple)

        for node in fairway.nodes:
            node.draw()


# Read all data
IO.read_data()

network = Network()
GlobalVars.network = network
# Simulation
GlobalVars.zoom = False
x_min = 3.140237
y_min = 50.794897
x_min, y_min = Utilities.normalize(x_min, y_min)
x_max = 3.371636
y_max = 50.865251
x_max, y_max = Utilities.normalize(x_max, y_max)
env = sim.Environment(trace=True)
if GlobalVars.zoom:
    env.animation_parameters(x0=x_min, x1=x_max, y0=y_min,
                             modelname="Alsic Waterway Simulation", animate=True,
                             background_color="lightgray")
else:
    env.animation_parameters(
        modelname="Alsic Waterway Simulation", animate=True,
        background_color="lightgray")
env.modelname("Alsic Waterway Simulation")
network.generate_graph()
network.draw_network()

# Generate the vessel
Vessel_generator()

env.run(100000)
