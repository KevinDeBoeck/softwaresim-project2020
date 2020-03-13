import IO
import simulation
from model.Bridge import Bridge
from model.FairwaySection import FairwaySection
from model.Lock import Lock
from model.Network import Network
from model.Terminal import Terminal


def read_data():
    """ Read all the relevant data"""

    simulation.trajectories_dict = IO.read_trajectories()
    simulation.df_passages = IO.read_passages()

    network = Network()

    network.trajectories = simulation.trajectories_dict
    simulation.network = network

    # Parse water
    print("Importing fairway sections")
    df_network = IO.read_network()
    for index, row in df_network.iterrows():
        xy = row.geometry[0].xy
        lon1 = xy[0][0]
        lat1 = xy[1][0]
        lon2 = xy[0][int(len(xy[0])) - 1]
        lat2 = xy[1][int(len(xy[1])) - 1]

        fairway_section = FairwaySection(row, lon1, lat1, lon2, lat2, xy)
        network.add_fairway_section(row["fw_code"], fairway_section)

    # Parse bridges
    print("Importing bridges")
    df_bridges = IO.read_bridges()
    for index, row in df_bridges.iterrows():
        geometry = df_bridges.geometry[index]
        point = geometry.bounds
        fw_code = row["fw_code"]
        bridge = Bridge(row, point[0], point[1])
        network.fairway_sections[fw_code].add_bridge(bridge)

    # Parse terminals
    print("Importing terminals")
    df_terminals = IO.read_terminals()
    for index, row in df_terminals.iterrows():
        geometry = df_terminals.geometry[index]
        point = geometry.bounds
        fw_code = row["fw_code"]
        terminal = Terminal(row, point[0], point[1])
        network.fairway_sections[fw_code].add_terminal(terminal)

    # Parse locks
    print("Importing locks")
    df_locks = IO.read_locks()
    for index, row in df_locks.iterrows():
        geometry = df_locks.geometry[index]
        point = geometry.bounds
        fw_code = row["sectionref"]
        lock = Lock(row, point[0], point[1])
        network.fairway_sections[fw_code].add_lock(lock)

    network.generate_network()
