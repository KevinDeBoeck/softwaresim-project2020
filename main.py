# Read the different data_queue_vessels_waiting_lock files
import random
import sys

import salabim as sim

import IO
from model import Utilities, GlobalVars
from model.CrossRoad import CrossRoadType
from model.Network import Network
from model.Vessel import VesselComponentGenerator

seeds = [321, 6301, 6348, 7315, 8456]

data_queue_vessels_in_network = []
bins_queue_vessels_in_network = []

data_queue_vessels_waiting_lock = []
bins_queue_vessels_waiting_lock = []

i = seeds[4]

# for i in seeds:
GlobalVars.seed = i
folder = 'crossroads'
name = 'smartsigns'

out_file = 'output/{}/{}_{}.txt'.format(folder, name, str(GlobalVars.seed))

random.seed(GlobalVars.seed)

# Read all data_queue_vessels_waiting_lock
IO.read_data()

network = Network()
GlobalVars.network = network
# Simulation
GlobalVars.crossroad_type = CrossRoadType.SmartSigns
GlobalVars.animate = False
GlobalVars.zoom = True
GlobalVars.x_min = 3.140237
GlobalVars.y_min = 50.794897
GlobalVars.x_min, GlobalVars.y_min = Utilities.normalize(GlobalVars.x_min, GlobalVars.y_min)
GlobalVars.x_max = 3.6
GlobalVars.x_max = 3.5
GlobalVars.y_max = 50.8
GlobalVars.x_max, GlobalVars.y_max = Utilities.normalize(GlobalVars.x_max, GlobalVars.y_max)
env = sim.Environment(trace=False, time_unit='minutes', random_seed=GlobalVars.seed)
GlobalVars.environment = env
if GlobalVars.zoom:
    env.animation_parameters(x0=GlobalVars.x_min, x1=GlobalVars.x_max, y0=GlobalVars.y_min,
                             modelname="Alsic Waterway Simulation", animate=GlobalVars.animate,
                             background_color="lightgray")
else:
    env.animation_parameters(
        modelname="Alsic Waterway Simulation", animate=GlobalVars.animate,
        background_color="lightgray")
env.modelname("Alsic Waterway Simulation")
network.generate_graph()
network.draw_network()
GlobalVars.init()

GlobalVars.update_counters()
GlobalVars.draw_legend()

env.suppress_trace_linenumbers(True)
# Generate the vessel
VesselComponentGenerator()
env.run()

save_stdout = sys.stdout
sys.stdout = open(out_file, 'w')

GlobalVars.queue_vessels_in_network.print_statistics()
GlobalVars.queue_vessels_in_network.length_of_stay.print_histogram()

GlobalVars.queue_vessels_waiting_segment.print_statistics()
GlobalVars.queue_vessels_waiting_segment.length_of_stay.print_histogram()

GlobalVars.queue_vessels_waiting_crossroad.print_statistics()
GlobalVars.queue_vessels_waiting_crossroad.length_of_stay.print_histogram()

GlobalVars.queue_vessels_waiting_bridge.print_statistics()
GlobalVars.queue_vessels_waiting_bridge.length_of_stay.print_histogram()

GlobalVars.queue_vessels_waiting_lock.print_statistics()
GlobalVars.queue_vessels_waiting_lock.length_of_stay.print_histogram()

tmp = GlobalVars.queue_vessels_in_network
bin_width, lowerbound, number_of_bins = tmp.length_of_stay.histogram_autoscale()

bins_queue_vessels_in_network.append(number_of_bins)
data_queue_vessels_in_network.append(tmp.length_of_stay.x())

tmp = GlobalVars.queue_vessels_waiting_lock
bin_width, lowerbound, number_of_bins = tmp.length_of_stay.histogram_autoscale()

bins_queue_vessels_waiting_lock.append(number_of_bins)
data_queue_vessels_waiting_lock.append(tmp.length_of_stay.x())
GlobalVars.reset()

# number_of_bins = max(bins_queue_vessels_in_network)
# new_data_queue_vessels_in_network = []
#
# for index in range(0, len(data_queue_vessels_in_network)):
#     new_data_queue_vessels_in_network.extend(data_queue_vessels_in_network[index])
#
# hist, bins = np.histogram(new_data_queue_vessels_in_network, bins=number_of_bins)
#
# hist = np.divide(hist, len(seeds))
#
# # for i, x in zip(seeds, data_queue_vessels_waiting_lock):
# plt.hist(bins[:-1], bins, weights=hist)
# plt.title("Network")
# plt.xlabel("Time in network")
# plt.ylabel("Frequency")
# plt.show()
#
# number_of_bins = max(bins_queue_vessels_waiting_lock)
# new_data_queue_vessels_waiting_crossroad = []
#
# for index in range(0, len(data_queue_vessels_waiting_lock)):
#     new_data_queue_vessels_waiting_crossroad.extend(data_queue_vessels_waiting_lock[index])
#
# hist, bins = np.histogram(new_data_queue_vessels_waiting_crossroad, bins=number_of_bins)
#
# hist = np.divide(hist, len(seeds))
#
# # for i, x in zip(seeds, data_queue_vessels_waiting_lock):
# plt.hist(bins[:-1], bins, weights=hist)
# plt.title("Lock")
# plt.xlabel("Time waiting at lock")
# plt.ylabel("Frequency")
# plt.show()
