import sys
sys.path.insert(0,"..")
import os

# get AMDA username and password from environement variables
username=os.environ["AMDA_USER"]
password=os.environ["AMDA_PASSWORD"]

# get functions for listing and getting user parameters
from amdapy.amda import AMDA

amda= AMDA()
# get list of users parameters
derived_params=amda.list_derived(username, password)
# loop over parameters and print description
for dp in derived_params:
    print(dp)
    data=amda.get_derived(username, password, dp.paramid, "2010-01-01T00:00:00","2010-02-01T00:00:00",sampling=43)
    print(data)
print()
print("List of derived parameters : {}".format([dp.name for dp in derived_params]))
