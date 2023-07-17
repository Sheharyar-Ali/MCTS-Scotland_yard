import pandas as pd
import numpy as np

file = open("Map_info.csv")
lines = file.readlines()
fixed = pd.DataFrame({})
Info =[]
for line in lines:
    buffer = []
    line=line[:-1]
    columns = line.split(",")
    if columns[0] != "id":
        buffer.append(int(columns[0]))
        buffer.append((0,0))
        col2 = columns[1]
        if col2 !="0":
            to_add = col2.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col3 = columns[2]
        if col3 !="0":
            to_add = col3.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        col4=columns[3]
        if col4 !="0":
            to_add = col4.split("/")
            for i in range(len(to_add)):
                to_add[i] = int(to_add[i])
            buffer.append(to_add)
        else:
            buffer.append([0])
        Info.append(buffer)


