import sys
sys.path.insert(0,"..")
from amdapy.amda import AMDA

amda=AMDA()
dd=amda.collection.find("tao-ura-sw")
print(dd)
