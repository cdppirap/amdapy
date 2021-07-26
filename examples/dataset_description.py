import sys
sys.path.insert(0,"..")
from amdapy.amda import AMDA

# just initialize connection to AMDA and try to retrieve the description of the tao-ura-sw dataset
amda=AMDA()
dd=amda.collection.find("tao-ura-sw")
print(dd)
