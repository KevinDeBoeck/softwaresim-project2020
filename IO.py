import json

import geopandas as gpd
import pandas as pd

import model.GlobalVars as Config
from model.Bridge import Bridge
from model.FairwaySection import FairwaySection
from model.Lock import Lock
from model.Trajectory import Trajectory
from model.Vessel import Vessel

trajectories_file = 'project_files/trajectories.geojson'
waterway_file = 'project_files/fairwaysections.geojson'  # All sections in flanders
bridges_file = 'project_files/bridges.geojson'
locks_file = 'project_files/locks.geojson'
terminals_file = 'project_files/terminals.geojson'
passages_file = 'project_files/passages_in.csv'

trajectory_dict = {}


def read_passages():
    """Read the different passages"""
    df_passages = pd.read_csv(passages_file, sep=';')

    # Get all the ships
    df_vessels = df_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(inplace=False)
    df_vessels = df_vessels.reset_index(drop=True)

    vessel_dict = {}
    vessels = []

    # Iterate over the vessels
    for index, row in df_vessels.iterrows():
        # Make a new object

        vessel = Vessel(row['ShipID'], row['Length'], row['Width'], row['CEMTKlasse'])
        vessel_dict[row['ShipID']] = vessel

    # Connect the route
    for index, row in df_passages.iterrows():
        # Get the corresponding vessel
        ship_id = row['ShipID']
        trajectory_name = row['TrajectName']

        trajectory = trajectory_dict.get(trajectory_name)
        vessel = vessel_dict.get(ship_id)
        vessel.trajectory_route.append(trajectory)

        # Try not to add the trajectory
        vessels.append(vessel)

    # for vessel in vessels:
    #     l = len(vessel.trajectory_route)
    #     for index, obj in enumerate(vessel.trajectory_route):
    #         current_trajectory = vessel.trajectory_route[index]
    #         if index < (l-1):
    #             next_trajectory = vessel.trajectory_route[index + 1]

    return vessels, vessel_dict


def read_trajectories():
    # read the trajectories

    f = open(trajectories_file)

    trajectories_df = gpd.read_file(trajectories_file)

    for index, row in trajectories_df.iterrows():
        trajectory_name = row['TrajectName']
        if trajectory_name in trajectory_dict:
            # It already exist
            trajectory = trajectory_dict.get(trajectory_name)
            trajectory.lon2 = row['LoLong']
            trajectory.lat2 = row['LoLat']

        else:
            lat1 = row['LoLat']
            lon1 = row['LoLong']
            # It does not exist, make the trajectory
            sectionref = row['sectionref']
            trajectory = Trajectory(lon1, lat1, trajectory_name)
            trajectory_dict[trajectory_name] = trajectory

    return trajectory_dict


def read_network():
    fairway_sections_list = []
    # read the waterway network

    with open(waterway_file) as f:
        data = json.load(f)

    for feature in data['features']:
        fw_code = feature['properties']['fw_code']
        coordinates = feature['geometry']['coordinates']

        fairway_section = FairwaySection(fw_code, coordinates)
        fairway_sections_list.append(fairway_section)

    return fairway_sections_list


def read_bridges():
    # read the waterway network
    bridges_df = gpd.read_file(bridges_file)
    bridges = []

    with open(bridges_file) as f:
        data = json.load(f)

    for feature in data['features']:
        # print(feature)
        fw_code = feature['properties']['fw_code']
        bridge = Bridge(fw_code, feature['geometry']['coordinates'])
        bridges.append(bridge)

    return bridges


def read_locks():
    # read the waterway network
    locks_df = gpd.read_file(locks_file)
    locks = []

    with open(locks_file) as f:
        data = json.load(f)

    for feature in data['features']:
        fw_code = feature['properties']['sectionref']
        lock = Lock(fw_code, feature['geometry']['coordinates'])
        locks.append(lock)

    return locks


def read_terminals():
    # read the waterway network
    terminals_df = gpd.read_file(terminals_file)
    return terminals_df


def read_data():
    """ Read all the relevant data"""

    Config.trajectories_dict = read_trajectories()

    # Read the fairway sections
    Config.fairway_section_list = read_network()

    # Read all the bridges in the network
    Config.bridges = read_bridges()

    # Read all the locks in the network
    Config.locks = read_locks()

    Config.vessels, Config.vessels_dict = read_passages()
