import random

import pandas as pd

trajectories_file = 'project_files/trajectories.geojson'
waterway_file = 'project_files/fairwaysections.geojson'  # All sections in flanders
bridges_file = 'project_files/bridges.geojson'
locks_file = 'project_files/locks.geojson'
terminals_file = 'project_files/terminals.geojson'
passages_file = 'project_files/passages_in.csv'

with open('project_files/passages_gen.csv', 'w') as file:
    file.write("TrajectName;ShipID;CEMTKlasse;Width;Length\n")

    df_passages = pd.read_csv(passages_file, sep=';')

    # Get all the ships
    df_vessels = df_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(subset='ShipID', keep='first')
    df_vessels = df_vessels.reset_index(drop=True)

    options = [
        ["Traject1", "Traject2", "Traject3", "Traject4", "Traject5", "Traject6"],
        ["Traject6", "Traject5", "Traject4", "Traject3", "Traject2", "Traject1"],
        ["Traject1", "Traject2", "Traject7"],
        ["Traject7", "Traject2", "Traject1"],
        ["Traject7", "Traject3", "Traject4", "Traject5", "Traject6"],
        ["Traject6", "Traject5", "Traject4", "Traject3", "Traject7"]
    ]

    for index, row in df_vessels.iterrows():
        choice = random.choice(options)
        for traject in choice:
            file.write(
                traject + ";" + row['ShipID'] + ";" + row['CEMTKlasse'] + ";" + str(
                    row['Width']) + ";" + str(row['Length']) + "\n")
