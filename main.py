# Read the different data files
from builtins import set

import setup
import salabim as sim
import simulation
from model.Vessel import VesselComponentGenerator

setup.read_data()

simulation.draw_trajectories = True
simulation.draw_scale = 10
simulation.draw_skip = 8


# Simulation
simulation.environment = sim.Environment(trace=False)
env = simulation.environment
env.animate(True)
env.modelname("Alsic Waterway Simulation")

simulation.network.draw_and_project()
simulation.network.generate_graph()

VesselComponentGenerator()

env.run()
