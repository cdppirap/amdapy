import os
import sys
sys.path.insert(0,"/home/aschulz/amdapy")
from amdapy.amda import AMDA
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import numpy as np
import pickle as pkl

def load_labels(filename):
  a=[]
  with open(filename,"r") as f:
    d=f.read()
    for line in d.split("\n"):
      ld=line.split(" ")
      # try to convert first two elements to datetime objects
      try:
        ld[0]=datetime.datetime.strptime(ld[0], "%Y-%m-%dT%H:%M:%S")
        ld[1]=datetime.datetime.strptime(ld[1], "%Y-%m-%dT%H:%M:%S")
        ld[2]=int(int(ld[2])!=0)
        a.append(ld[:3])
      except:
        pass
  return np.array(a)
def get_train_data(start, stop):
  amda=AMDA()
  parameter_id="al"
  parameter_desc=amda.collection.find(parameter_id)
  dataset_desc=amda.collection.find(parameter_desc.dataset_id)
  dataset=amda.get(dataset_desc, start=start, stop=stop)
  return dataset["AL"][:]
def get_local_minima(x):
  a=[]
  n=x.shape[0]
  for i in range(n):
    if i==0:
      if x[i]<x[1]:
        a.append([i,x[i]])
    elif i==n-1:
      if x[i]<x[i-1]:
        a.append([i,x[i]])
    else:
      if x[i]<x[i-1] and x[i]<x[i+1]:
        a.append([i,x[i]])
  return np.array(a)
def plot_hist(x,bins=1000, title=None):
  plt.figure()
  if not title is None:
    plt.title(title)
  plt.hist(x, bins=bins)
  plt.show()
# label file
label_filename="/home/aschulz/amdapy/tests/ML_GTL_IsSOR_AL_cat_0.txt"
labels=load_labels(label_filename)
print("Number of events in label file : {}".format(labels.shape[0]))
print("First event                    : {}".format(labels[0,:]))
print("Last event                     : {}".format(labels[-1,:]))
# take data from 5 hours before and after the event bounds (start of first event and end of last)
default_timedelta=timedelta(hours=5)
data_start=labels[0,0]-default_timedelta
data_stop=labels[-1,1]+default_timedelta
print("Getting data from {} to {}".format(data_start, data_stop))
# get training data
if not os.path.exists("train_data.pkl"):
  train_data=get_train_data(data_start, data_stop)
  pkl.dump(train_data, open("train_data.pkl","wb"))
else:
  train_data=pkl.load(open("train_data.pkl","rb"))
train_data_np=train_data.to_numpy()
diff_train_data=np.diff(train_data_np)
print("Training data shape : {}".format(train_data.shape))
# count local minima
local_min=get_local_minima(train_data)
print("Local minima in train data : {}".format(local_min.shape[0]))
diff_local_min=get_local_minima(diff_train_data)
print("Local minima in diff of train data : {}".format(diff_local_min.shape[0]))
# plot local minima value distribution
plot_hist(train_data_np[local_min[:,0].astype(int)], title="local min dist in train data")
plot_hist(diff_train_data[diff_local_min[:,0].astype(int)], title="diff local min dist in train data")
# check the local minima position in increasing order
increasing_value_local_min=local_min[np.argsort(local_min[:,1]),:]
print(increasing_value_local_min[:10,:])
# plot training data an place vertical line on the first 76 local minima (sorted by increasing value)
f, (ax1, ax2) = plt.subplots(2,1,sharex=True)
ax1.plot(train_data)
#plt.vlines(increasing_value_local_min[:76,0], -1000, 1000)
for i in range(76):
  ax1.axvline(train_data.index[increasing_value_local_min[i,0].astype(int)],c="r")
for i in range(labels.shape[0]):
  ax1.axvline(labels[i,0],c="b")
  ax1.axvline(labels[i,1],c="g")
from scipy import stats
w_s=100
print("doing normal tests")
a=np.array([stats.normaltest(np.diff(train_data[i-w_s:i+w_s]))[1] for i in range(w_s,train_data.shape[0]-w_s)])
print("done")
pos_pos=train_data<0.
tmp=train_data[pos_pos]
aa=np.abs(np.diff(tmp))/tmp[:-1]
ax2.plot(train_data.index[w_s:-w_s],a)
f.autofmt_xdate()

plt.show()
exit()
# plot the training data and the corresponding events
fig=plt.figure()
plt.title("Training data : AL index")
plt.xlabel("Time")
plt.ylabel("AL (nT)")
plt.plot(train_data)
fig.autofmt_xdate()
plt.show()
exit()
amda=AMDA()

parameter_id="al"
parameter_desc=amda.collection.find(parameter_id)
dataset_desc=amda.collection.find(parameter_desc.dataset_id)
start=dataset_desc.starttime
start=datetime.datetime(year=2008, month=1, day=4, hour=6 , minute=0)
dataset=amda.get(dataset_desc, start=start, stop=start+timedelta(hours=4))

print(dataset)

import numpy as np

# label file /mlPlasmas-model-substorms/data/...
al=dataset["AL"][:].to_numpy()
au=dataset["AU"][:].to_numpy()
ao=dataset["AO"][:].to_numpy()
ae=dataset["AE"][:].to_numpy()

print("al shape {}".format(al.shape))
print("au shape {}".format(au.shape))
print("al nans : {}".format(np.sum(np.isnan(al))/al.shape[0]))
print("au nans : {}".format(np.sum(np.isnan(au))/au.shape[0]))
print("ao nans : {}".format(np.sum(np.isnan(ao))/ao.shape[0]))
print("ae nans : {}".format(np.sum(np.isnan(ae))/ae.shape[0]))
dataset["AL"].plot()
plt.show()
