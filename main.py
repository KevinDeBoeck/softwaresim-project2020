# Read the different data files
from builtins import set

import IO
import setup
import salabim as sim


def read_data():
    """ Read all the relevant data"""
    global trajectories_dict
    global df_network
    global df_network_totalbounds
    global df_bridges
    global df_terminal
    global df_passages

    trajectories_dict = IO.read_trajectories()
    df_network = IO.read_network()
    df_network_totalbounds = IO.read_network()
    df_bridges = IO.read_bridges()
    df_terminal = IO.read_terminals()
    df_passages = IO.read_passages()


# Read all data
read_data()

# Simulation
env = sim.Environment(trace=True)
env.animate(True)
env.modelname("Alsic Waterway Simulation")

setup.draw_network(env,df_network.geometry)



env.run(100)
