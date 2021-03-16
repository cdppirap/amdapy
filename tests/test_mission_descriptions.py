from amdapy.amda import AMDA

amda = AMDA()

for mission in amda.collection.iter_mission():
    print(mission)

