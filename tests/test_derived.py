import sys
sys.path.insert(0, "..")

from amdapy.amdaWSClient.client import get_derived, list_derived

derived_params=list_derived("schulz", "sirapass")
for dp in derived_params:
    print(dp)
print("List of derived parameters : {}".format([dp.name for dp in derived_params]))
