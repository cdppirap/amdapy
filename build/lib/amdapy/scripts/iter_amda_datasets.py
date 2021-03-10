"""
:author: Alexandre Schulz
:file: iter_amda_datasets.py

Simple script for testing the implementation of the amda dataset iterator
"""
import sys
sys.path.insert(0,"/home/aschulz")
from amdapy.amdaWSClient.client import get_obs_tree
from amdapy.session import Session
import datetime

format="%Y-%m-%dT%H:%M:%SZ"
if __name__=="__main__":
  print("Testing AMDA iter datasets")
  amda_tree=get_obs_tree()
  for d in amda_tree.iter_dataset():
    # get the dataset timespan
    start,stop=d.timespan()
    print(d.id,start,stop)
    print(d)
