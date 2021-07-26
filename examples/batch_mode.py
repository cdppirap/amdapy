import sys
sys.path.insert(0,"..")
import os

# get functions for listing and getting user parameters
from amdapy.amda import AMDA

amda= AMDA()
# dataset description
dataset_description = amda.collection.find("ace-imf-all")
print(dataset_description)
# get dataset over 10 years
dataset = amda.get(dataset_description, start="1998-01-01T00:00:00",stop="2008-01-01T00:00:00")
print(dataset.data)
print("index duplicates : {}".format(dataset.data.index.duplicated().sum()))
