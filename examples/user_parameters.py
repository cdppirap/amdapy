import sys
sys.path.insert(0,"..")
import os

# get AMDA username and password from environement variables
username=os.environ["AMDA_USER"]
password=os.environ["AMDA_PASSWORD"]

# get functions for listing and getting user parameters
from amdapy.rest.client import get_derived, list_derived

# get list of users parameters
derived_params=list_derived(username, password)
# loop over parameters and print description
for dp in derived_params:
    print(dp)

print()
print("List of derived parameters : {}".format([dp.name for dp in derived_params]))
