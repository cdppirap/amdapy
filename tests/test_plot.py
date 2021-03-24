import matplotlib.pyplot as plt
import sys
sys.path.insert(0,"/home/aschulz/amdapy")

from amdapy.amda import AMDA

amda=AMDA()

dataset_id="tao-ura-sw"
dataset_desc=amda.collection.find(dataset_id)
dataset=amda.get(dataset_desc)
dataset["velocity"].plot(dataset_id="tao-ura-sw")
plt.show()
