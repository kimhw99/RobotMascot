import pickle
import numpy as np
import os
import json

data = dict()

for f in os.listdir(path="files"):
    if f.endswith('pkl'):
        data[f.replace('.pkl', '').replace('kinematics', '').replace('_', ' ').rstrip()] = f

with open('movements.json', 'w') as f:
    json.dump(data, f)

with open('files/captain_america_shield_kinematics.pkl', 'rb') as file:
    data = pickle.load(file)
    print(type(data))

print(data)

for d in data:
    print(d)