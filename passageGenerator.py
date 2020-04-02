import pandas as pd

from model.Vessel import Vessel

trajectories_file = 'project_files/trajectories.geojson'
waterway_file = 'project_files/fairwaysections.geojson'  # All sections in flanders
bridges_file = 'project_files/bridges.geojson'
locks_file = 'project_files/locks.geojson'
terminals_file = 'project_files/terminals.geojson'
passages_file = 'project_files/passages_in.csv'

with open('project_files/passages_gen.csv', 'a') as file:
    file.write("TrajectName;ShipID;CEMTKlasse;Width;Length\n")

    df_passages = pd.read_csv(passages_file, sep=';')

    # Get all the ships
    df_vessels = df_passages[['ShipID', 'CEMTKlasse', 'Width', 'Length']].drop_duplicates(inplace=False)
    df_vessels = df_vessels.reset_index(drop=True)

    for index, row in df_vessels.iterrows():
        for idx in range(1, 3):
            file.write(
                "Traject" + str(idx) + ";" + row['ShipID'] + ";" + row['CEMTKlasse'] + ";" + str(row['Width']) + ";" +
                str(row['Length']) + "\n")
