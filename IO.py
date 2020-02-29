import geopandas as gpd
import pandas as pd
import sys

import simulation
from model.Vessel import Vessel
from model.Trajectory import Trajectory

trajectories_file = 'project_files/trajectories.geojson'
waterway_file = 'project_files/fairwaysections.geojson'  # All sections in flanders
bridges_file = 'project_files/bridges.geojson'
terminals_file = 'project_files/terminals.geojson'
passages_file = 'project_files/passages_in.csv'

trajectory_dict = {}


def read_passages():
    """Read the different passages"""
    df_passages = pd.read_csv(passages_file, sep=';')

    # Get all the ships
    df_vessels = df_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(inplace=False)
    df_vessels = df_vessels.reset_index(drop=True)

    # Make a global vessel dict
    global vessel_dict
    vessel_dict = {}
    simulation.vessels_dict = vessel_dict

    # Iterate over the vessels
    for index, row in df_vessels.iterrows():
        # Make a new object

        vessel = Vessel(row['ShipID'], row['Length'], row['Width'], row['CEMTKlasse'])
        vessel_dict[row['ShipID']] = vessel

    # Connect the route
    for index, row in df_passages.iterrows():
        # Get the corresponding vessel
        shipId = row['ShipID']
        trajectoryName = row['TrajectName']

        trajectory = trajectory_dict.get(trajectoryName)
        vessel = vessel_dict.get(shipId)
        vessel.route.append(trajectory)

    # print()


def read_trajectories():
    # read the trajectories

    f = open(trajectories_file)

    # with open(trajectories) as jsonfile:
    #    data = json.load(jsonfile)
    #    print(data)
    # pass

    trajectories_df = gpd.read_file(trajectories_file)
    # print(trajectories_df.head())
    # print(trajectories_df['LoLat'])

    global trajectories_dict

    for index, row in trajectories_df.iterrows():
        # print(row['LoLat'], row['LoLong'])

        trajectoryName = row['TrajectName']
        if trajectoryName in trajectory_dict:
            # It already exist
            trajectory = trajectory_dict.get(trajectoryName)
            trajectory.lon2 = row['LoLong']
            trajectory.lat2 = row['LoLat']

        else:
            lat1 = row['LoLat']
            lon1 = row['LoLong']
            # It does not exist, make the trajectory
            trajectory = Trajectory(lon1, lat1)
            trajectory_dict[trajectoryName] = trajectory

    return trajectory_dict


def read_network():
    # read the waterway network
    network_df = gpd.read_file(waterway_file)
    return network_df


def read_bridges():
    # read the waterway network
    bridges_df = gpd.read_file(bridges_file)
    return bridges_df


def read_terminals():
    # read the waterway network
    terminals_df = gpd.read_file(terminals_file)
    return terminals_df
