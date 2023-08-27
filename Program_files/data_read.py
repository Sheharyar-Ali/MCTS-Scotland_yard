import math

import pandas as pd
import numpy as np

# Import data about the stations
file = open("../data_files/Map_info.csv")
lines = file.readlines()
Info = []
Q_values = []
Visits = []
loc_cat = []
for line in lines:
    buffer = []
    line = line[:-1]
    columns = line.split(",")
    if columns[0] != "id":
        buffer.append(int(columns[0]))
        Visits.append([int(columns[0]), 0])
        buffer.append((int(columns[1]), int(columns[2])))
        col2 = columns[3]
        if col2 != "0":
            to_add = col2.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col3 = columns[4]
        if col3 != "0":
            to_add = col3.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col4 = columns[5]
        if col4 != "0":
            to_add = col4.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        Info.append(buffer)
file.close()

# Get Q-value data from a file
Q_Values_df = pd.DataFrame(columns=["origin", "destination", "transport", "value"])
for data in Info:
    current_station = data[0]
    for i in range(2, len(data)):
        if data[i] != [0]:
            for j in range(len(data[i])):
                node = [current_station, data[i][j], i - 2, 0]
                Q_values.append([current_station, data[i][j], i - 2, 0])
                Q_Values_df.loc[len(Q_Values_df)] = node

# Update q values
file = open("../data_files/q_values.csv")
lines = file.readlines()
for line in lines:
    line = line[:-1]
    columns = line.split(",")
    columns = columns[1:]
    if columns[0] != "origin":
        for i in range(0, 3):
            columns[i] = math.trunc(float(columns[i]))
        columns[3] = float(columns[3])
        for i in range(len(Q_values)):
            node = Q_values[i]
            if columns[0] == node[0] and columns[1] == node[1] and columns[2] == node[2] and columns[3] != 0:
                node[3] = columns[3]
                Q_Values_df["value"][i] = node[3]
file.close()

# Get location categorisation data
Loc_file = open("../data_files/Location_categorisation.csv")
lines = Loc_file.readlines()
for line in lines:
    line = line[:-1]
    line = line.split(",")
    if line[0] != "a":
        loc_cat.append([int(line[0]), int(line[1])])


def Get_statistics(file_name, case):
    file = open(file_name)
    lines = file.readlines()
    data = pd.DataFrame(columns=["Caught", "Rounds", "Coverage"])
    var_win = []
    var_cov = []
    for line in lines:
        line = line[:-1]
        columns = line.split(",")
        if columns[-1] == case:
            data.loc[len(data)] = [columns[2], int(columns[3]), float(columns[10])]
    print(data)
    win_rate = len(data[data["Caught"] == "TRUE"]) / len(data)
    mean_rounds = data["Rounds"].mean(axis=0)
    mean_coverage = data["Coverage"].mean(axis=0)
    mean_coverage_full_games = data[data["Caught"] == "TRUE"]["Coverage"].mean(axis=0)
    for i in range(len(data)):
        entry = data.iloc[i]
        if entry["Caught"] == "TRUE":
            var_win.append((1 - win_rate) ** 2 )
        else:
            var_win.append((0 - win_rate) ** 2 )
        var_cov.append((entry["Coverage"] - mean_coverage)**2 / (len(data) - 1))
    std_win = np.sqrt(np.sum(np.array(var_win)) / (len(data) - 1))
    std_cov = np.sqrt(np.sum(np.array(var_cov)) / (len(data) - 1))

    return win_rate * 100, mean_rounds, mean_coverage * 100, mean_coverage_full_games * 100, std_win * 100 , std_cov * 100
