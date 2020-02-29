# Read the different data files
from builtins import set

import setup
import salabim as sim
import simulation
from model.Vessel import VesselComponentGenerator

setup.read_data()

simulation.draw_scale = 10

# Simulation
simulation.environment = sim.Environment(trace=True)
env = simulation.environment
env.animate(True)
env.modelname("Alsic Waterway Simulation")

setup.draw_network()

VesselComponentGenerator()

env.run()
