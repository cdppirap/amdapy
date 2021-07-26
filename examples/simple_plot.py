import os
import sys
sys.path.insert(0, "..")


from amdapy.amda import AMDA

# connect to AMDA
amda=AMDA()

# get dataset description 
dataset_description=amda.collection.find("tao-ura-sw")
print(dataset_description)

# get the dataset's contents
dataset=amda.get(dataset_description)
print(dataset)

# object type
print(type(dataset.data))

# user can access parameters by using bracket operator
print(dataset["density"])
print(type(dataset["density"]))

# simple plot
import matplotlib.pyplot as plt
fig=dataset["density"].plot(dataset_id="tao-ura-sw")
plt.show()
