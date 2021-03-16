import sys
sys.path.insert(0,"/home/aschulz/amdapy")
import matplotlib.pyplot as plt

import amdapy
from amdapy.amda import AMDA

amda = AMDA()

dataset_id="tao-ura-sw"
dataset_desc=amda.collection.find(dataset_id)
print(dataset_desc)

# get the data
dataset = amda.get(dataset_desc)
print(dataset)
print(dataset.data)
print(dataset["velocity"])

fig = dataset["velocity"].plot()
plt.show()
