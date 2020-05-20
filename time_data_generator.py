import datetime

import pandas as pd

from model.Vessel import Vessel


def read_passages():
    format_str = '%Y-%m-%d %H:%M:%S.%f'

    """Read the different passages"""
    bad_passages = pd.read_csv("project_files/passages_in_v3_working.csv", sep=";")

    # Get all the ships
    df_vessels = bad_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(inplace=False)
    df_vessels = df_vessels.reset_index(drop=True)

    vessel_dict = {}

    # Iterate over the vessels
    for index, row in df_vessels.iterrows():
        # Make a new object

        height = 1

        vessel = Vessel(row['ShipID'], row['Length'], row['Width'], height, row['CEMTKlasse'])
        vessel_dict[row['ShipID']] = vessel

    # Connect the route
    for index, row in bad_passages.iterrows():
        # Get the corresponding vessel
        ship_id = row['ShipID']
        trajectory_time_string = row['Timestamp']
        trajectory_time = datetime.datetime.strptime(trajectory_time_string, format_str)

        vessel = vessel_dict.get(ship_id)
        vessel.trajectory_route.append(trajectory_time)

    return vessel_dict


def get_between_time(vessels):
    between_times = []
    prev = vessels.pop(0)
    while len(vessels) > 0:
        curr = vessels.pop(0)
        diff = curr.trajectory_route[0] - prev.trajectory_route[0]
        minutes = diff.seconds / 60
        if minutes < 200:
            between_times.append(minutes)
        prev = curr
    return between_times


vessels = read_passages()
vessels_list = list(vessels.values())
vessels_list = sorted(vessels_list, key=lambda vessel: vessel.trajectory_route[0])

between_times = get_between_time(vessels_list)

with open("times.csv", "w") as fp:
    tmp = ['{:.2f}'.format(item) for item in between_times]
    fp.write('\n'.join(tmp))
