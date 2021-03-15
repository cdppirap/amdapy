import sys
#sys.path.insert(0,"/home/aschulz/amdapy")
from amdapy.amda import AMDA

amda=AMDA()
dataset_id="tao-ura-sw"
dataset_desc=amda.collection.find(dataset_id)
dataset=amda.get(dataset_desc)
print(">>>dataset")
print(dataset)
print(">>>dataset[:]")
print(dataset[:])
print(">>>dataset[\"density\"]")
print(dataset["density"])

# get_parameter
parameter_id="ura_sw_n"
parameter_desc=amda.collection.find(parameter_id)
print(">>> parameter_desc")
print(parameter_desc)
parameter=amda.get(parameter_desc)
print(">>> parameter")
print(parameter)
print(">>> parameter[:]")
print(parameter[:])

# amdapy.amda.Dataset.iter_parameter
print(">>> [p.name for p in dataset.iter_parameter()]")
print([p.name for p in dataset.iter_parameter()])
print(">>> [p.units for p in dataset.iter_parameter()]")
print([p.units for p in dataset.iter_parameter()])

# amdapy.amda.Dataset.time
T=dataset.time()
print(">>> type(T)")
print(type(T))
print(">>> T")
print(T)

# Tutorial
dataset_description = amda.collection.find("tao-ura-sw")
print(">>> dataset_description")
print(dataset_description)
dataset=amda.get(dataset_description)
print(">>> dataset")
print(dataset)
print(">>> type(dataset.data)")
print(type(dataset.data))

from amdapy.amda import Timespan
import datetime
time_interval = Timespan(dataset_description.starttime, dataset_description.starttime+datetime.timedelta(days=10))
dataset = amda.get(dataset_description, time_interval)
print(">>> dataset.data.shape")
print(dataset.data.shape)


# simple plot
import matplotlib.pyplot as plt
parameter=dataset["density"]
fig=plt.figure()
plt.plot(parameter[:])
plt.title("dataset: {} / param: {}".format("tao-ura-sw", parameter.name))
plt.xlabel("Time")
plt.grid(True)
plt.ylabel("{} ({})".format(parameter.name, parameter.units))
fig.autofmt_xdate()
plt.savefig(sys.argv[0]+".png")
#plt.show()
