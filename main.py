# Read the different data files
from builtins import set

import setup
import salabim as sim
import simulation
from model.Vessel import VesselComponentGenerator

setup.read_data()

simulation.zoomed = True
simulation.detailed_map = True
simulation.draw_trajectories = False
if simulation.zoomed:
    simulation.draw_scale = 10
else:
    simulation.draw_scale = 1

# Simulation
simulation.environment = sim.Environment(trace=False)
env = simulation.environment
env.animate(True)
env.modelname("Alsic Waterway Simulation")

setup.draw_network()

VesselComponentGenerator()

env.run()
