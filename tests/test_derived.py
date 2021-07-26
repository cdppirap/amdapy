import sys
sys.path.insert(0,"..")
import os

username=os.environ["AMDA_USER"]
password=os.environ["AMDA_PASSWORD"]

from amdapy.rest.client import get_derived, list_derived

derived_params=list_derived(username, password)
for dp in derived_params:
    print(dp)
print("List of derived parameters : {}".format([dp.name for dp in derived_params]))
