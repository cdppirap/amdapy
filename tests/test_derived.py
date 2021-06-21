import sys
sys.path.insert(0, "..")

from amdapy.amdaWSClient.client import get_derived, list_derived

derived_params=list_derived("schulz", "sirapass")
print("List of derived parameters : {}".format(derived_params))
