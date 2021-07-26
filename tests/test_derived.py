import os
import sys
sys.path.insert(0, "..")

username=os.env["AMDA_USER"]
password=os.env["AMDA_PASSWORD"]
from amdapy.amdaWSClient.client import get_derived, list_derived

derived_params=list_derived(username, password)
for dp in derived_params:
    print(dp)
print("List of derived parameters : {}".format([dp.name for dp in derived_params]))
