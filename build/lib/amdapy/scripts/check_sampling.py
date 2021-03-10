"""
:author: Alexandre Schulz
:file: Check amda dataset sampling
"""

import amdapy
from amdapy.vidata import VIDataset

import argparse

if __name__=="__main__":
  parser=argparse.ArgumentParser()
  parser.add_argument("input",type=str,help="dataset path")
  parser.add_argument("--plot",help="plot sampling histogram",action="store_true")
  args=parser.parse_args()
  # create amda dataset object
  dataset=VIDataset(args.input)
  print("Checking sampling of VIDataset at {}".format(args.input))
  s_m=[None,None]
  for ds in dataset.iter():
    s=ds.get_sampling()
    if s is None:
      continue
    [a,b]=s
    if s_m[0] is None:
      s_m[0]=a
    else:
      if a<s_m[0]:
        s_m[0]=a
    if s_m[1] is None:
      s_m[1]=b
    else:
      if b>s_m[1]:
        s_m[1]=b
  print("Sampling : {}".format(s_m))
  
  if args.plot:
    import matplotlib.pyplot as plt
    import numpy as np
    a=None
    for ds in dataset.iter():
      t=ds.get_time()
      if t is None:
        continue
      diff=np.diff(t)
      if diff.shape[0]==0:
        continue
      if a is None:
        a=diff
      else:
        a=np.concatenate((a,diff),axis=0)
    M=np.max(a)
    plt.figure()
    plt.hist(a,bins=int(M/100))
    plt.show()
  
