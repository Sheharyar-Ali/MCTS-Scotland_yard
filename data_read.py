import pandas as pd
import numpy as np

file = open("Map_info.csv")
lines = file.readlines()
fixed = pd.DataFrame({})
Info =[]
Q_values =[]
Visits=[]
for line in lines:
    buffer = []
    line=line[:-1]
    columns = line.split(",")
    if columns[0] != "id":
        buffer.append(int(columns[0]))
        Visits.append([int(columns[0]), 0])
        buffer.append((int(columns[1]),int(columns[2])))
        col2 = columns[3]
        if col2 !="0":
            to_add = col2.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col3 = columns[4]
        if col3 !="0":
            to_add = col3.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col4=columns[5]
        if col4 !="0":
            to_add = col4.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        Info.append(buffer)

for data in Info:
    current_station = data[0]
    for i in range(2,len(data)):
        if data[i] != [0]:
            for j in range(len(data[i])):
                Q_values.append([current_station, data[i][j], i-2, 0])




