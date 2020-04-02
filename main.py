# Read the different data files
import salabim as sim

import IO
from model import Utilities, GlobalVars
from model.Network import Network
from model.Vessel import VesselComponentGenerator

# Read all data
IO.read_data()

network = Network()
GlobalVars.network = network
# Simulation
GlobalVars.zoom = True
GlobalVars.x_min = 3.140237
GlobalVars.y_min = 50.794897
GlobalVars.x_min, GlobalVars.y_min = Utilities.normalize(GlobalVars.x_min, GlobalVars.y_min)
GlobalVars.x_max = 3.6
GlobalVars.y_max = 50.8
GlobalVars.x_max, GlobalVars.y_max = Utilities.normalize(GlobalVars.x_max, GlobalVars.y_max)
env = sim.Environment(trace=False, time_unit='minutes')
GlobalVars.environment = env
if GlobalVars.zoom:
    env.animation_parameters(x0=GlobalVars.x_min, x1=GlobalVars.x_max, y0=GlobalVars.y_min,
                             modelname="Alsic Waterway Simulation", animate=True,
                             background_color="lightgray")
else:
    env.animation_parameters(
        modelname="Alsic Waterway Simulation", animate=True,
        background_color="lightgray")
env.modelname("Alsic Waterway Simulation")
network.generate_graph()
network.draw_network()

GlobalVars.update_counters()


env.suppress_trace_linenumbers(True)
# Generate the vessel
VesselComponentGenerator()

env.run()
