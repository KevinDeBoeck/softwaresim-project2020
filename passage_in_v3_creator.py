import pandas as pd
from model.Vessel import Vessel


def read_passages():
    """Read the different passages"""
    bad_passages = pd.read_csv("project_files/passages_in_v2.csv", sep=";")

    # Get all the ships
    df_vessels = bad_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(inplace=False)
    df_vessels = df_vessels.reset_index(drop=True)

    vessel_dict = {}
    vessels = []

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
        trajectory_data = row

        vessel = vessel_dict.get(ship_id)
        vessel.trajectory_route.append(trajectory_data)

    return vessel_dict


def fix_data(vessels):
    new_data = []
    index = 0
    for vessel in vessels.values():
        first_line = vessel.trajectory_route.pop(0)
        first_line["ShipID"] = index
        new_data.append(first_line)
        if len(vessel.trajectory_route) > 0:
            second_line = vessel.trajectory_route.pop(0)
            accending = first_line["TrajectName"] < second_line["TrajectName"]
            second_line["ShipID"] = index
            new_data.append(second_line)

            prev = second_line
            while len(vessel.trajectory_route) > 0:
                curr = vessel.trajectory_route.pop(0)
                if prev["TrajectName"] < curr["TrajectName"]:
                    if accending:
                        curr["ShipID"] = index
                        new_data.append(curr)
                    else:
                        index += 1
                        accending = False
                        curr["ShipID"] = index
                        new_data.append(curr)
                if prev["TrajectName"] > curr["TrajectName"]:
                    if not accending:
                        curr["ShipID"] = index
                        new_data.append(curr)
                    else:
                        index += 1
                        accending = True
                        curr["ShipID"] = index
                        new_data.append(curr)
                prev = curr
        index += 1
    return new_data


vessels = read_passages()

new_rows_list = fix_data(vessels)

new_dataframe = pd.DataFrame(new_rows_list)

new_dataframe.to_csv("project_files/passages_in_v3.csv", index=False, sep=";")
