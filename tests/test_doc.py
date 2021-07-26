import os
import sys
sys.path.insert(0, "..")


from amdapy.amda import AMDA

amda=AMDA()

dataset_description=amda.collection.find("tao-ura-sw")
print(dataset_description)

dataset=amda.get(dataset_description)
print(dataset)

print(type(dataset.data))

print(dataset["density"])

import matplotlib.pyplot as plt
fig=dataset["density"].plot(dataset_id="tao-ura-sw")
plt.show()
