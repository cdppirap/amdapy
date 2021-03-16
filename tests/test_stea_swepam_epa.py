import sys
sys.path.insert(0,"/home/aschulz/amdapy")
import amdapy
from amdapy.amda import AMDA, Timespan
import datetime

tdelta=datetime.timedelta(days=2)
amda = AMDA()
parameter_id="psp_spi_aee"
parameter_description=amda.collection.find(parameter_id)
print("parameter descrition :\n{}".format(parameter_description))

# get the time 
dataset_description=amda.collection.find(parameter_description.dataset_id)
t0=dataset_description.starttime+tdelta
t1=t0+tdelta
tinterval=Timespan(t0,t1)
print("getting data from {} to {}".format(t0,t1))
parameter_data=amda.get(parameter_description, tinterval)
print(parameter_data)
print(parameter_data.data)

# print columns names
print(parameter_data.data.columns)
