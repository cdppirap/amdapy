"""
:author: Alexandre Schulz
:file: ace_swepam_stea.py
Download the ACE SWEPAM Electron Pitch angle data
"""
import os
import sys
import time
import argparse
import sys
import requests
from netCDF4 import Dataset
import numpy as np
import re

from amdapy.ddtime import DDTime, dt_to_seconds

spaces_re="[0-9]+x"

from amdapy.http_index import HTTPIndex

stea_index_root="http://www.srl.caltech.edu/ACE/ASC/DATA/level3/swepam/data"

def parse_args():
  parser=argparse.ArgumentParser()
  parser.add_argument("-i","--index", help="root of the data index", type=str, default="")
  parser.add_argument("-d","--destination", help="destination folder", type=str, default="")
  parser.add_argument("-b", "--brief", help="brief", type=str, default="")
  return parser.parse_args()

def get_dat_format_string(dat_content):
  for line in dat_content.split("\n"):
    if line.startswith("# format:"):
      l=line.split(":")[-1]
      while l.startswith(" "):
        l=l[1:]
      return l[1:-1]
  return None
def dat_parse_line(line, format):
  if len(line)==0:
    return None
  if line.startswith("#"):
    return None
  A=np.array(list(filter(None, line.split(" "))), dtype=object)
  ddtime="{}{}{}{}{}{}".format(A[0],A[1],A[2],A[3],A[4],"000")
  # convert to a datetime object
  B=[float(w) for w in A[-20:]]
  B=[DDTime.to_datetime(ddtime)]+B
  B=np.array(B,dtype=object)
  return B
  return None
def dat_to_netcdf(dat_content, destination, brief):
  # read the dat content and create a corresponding netCDF dataset object that can be saved.
  # get the format
  dat_format_str=get_dat_format_string(dat_content)
  data=[]
  if dat_format_str is None:
    print("Could not find a format string in content")
    return None
  for line in dat_content.split("\n"):
    l_data=dat_parse_line(line, dat_format_str)
    if not l_data is None:
      data.append(l_data)
  data=np.array(data)
  # get the data timespan
  ti,tf=data[0,0],data[-1,0]
  
  # get the date as a seconds
  ts=np.array([dt_to_seconds(k) for k in data[:,0]])
  # check that the time vector is correctly sorted
  if not ts[0]==np.min(ts):
    print("Error : first element of time vector is not the minimum")
    return None
  ddti=DDTime.from_datetime(ti)
  # now that we have the data we can create the NetCDF Dataset object
  # first define the name of the file as <brief>_<start_ddtime>.nc
  _ddti=ddti
  if _ddti.endswith("\0"):
    _ddti=_ddti[:-1]
  filename="{}_{}.nc".format(brief,_ddti) 
  _filename=os.path.join(destination,filename)
  print("Destination filename : {}".format(filename))
  if len(filename)>17:
    print("ERROR : filename {} is too long.".format(filename))
    rl=17-len(brief)-3
    filename="{}_{}.nc".format(brief, _ddti[:rl])
    print("\tnew filename : {}".format(filename))
  dataset=Dataset(_filename,mode="w",format="NETCDF3_CLASSIC")
  # create the appropriate dimensions : TimeLength=32, Time=None, dim1=20
  dimensions={"TimeLength":17,"Time":None,"dim1":20}
  for k in dimensions:
    dataset.createDimension(k, dimensions[k])
  variables={"Time":("Time",np.float64), "StartTime":("TimeLength","c"), "StopTime":("TimeLength","c"), "var1":(("Time","dim1"),np.float64)}
  for k in variables:
    dataset.createVariable(k, variables[k][1],variables[k][0])
  # set the time variable data
  dataset.variables["Time"][:]=ts
  # set the var1 data
  dataset.variables["var1"][:]=data[:,1:]
  # set start and stop time
  sddt=DDTime.from_datetime(ti)
  dataset.variables["StartTime"][:]=sddt
  dataset.variables["StopTime"][:]=DDTime.from_datetime(tf)
  # save the dataset
  dataset.sync()
  return 0
  
def run_function_with_done_print(func, str_, args):
  sys.stdout.write(str_)
  sys.stdout.flush()
  t0=time.time()
  r=func(*args)
  t0=time.time()-t0
  sys.stdout.write("done in {} seconds\n".format(t0))
  sys.stdout.flush()
  return r
if __name__=="__main__":
  args=parse_args()
  if args.index=="":
    args.index=stea_index_root
  if args.destination=="":
    args.destination="ace_swepam_stea"
  # if the destination path does not exist then create it
  if not os.path.exists(args.destination):
    os.system("mkdir -p {}".format(args.destination))
  if args.brief=="":
    args.brief="stea"
  # create the index manager
  index=HTTPIndex(args.index)
  # for keeping track of the progress it is interesting to count the number of urls
  print("Counting urls...")
  N=len([url for url in index.iter_url(recursive=True)])
  print("\t{} urls found in index".format(N))
  # iterate over the files and print the corresponding url
  prog=0
  for url in index.iter_url(recursive=True):
    print("Progress : {:.2f}".format(100*float(prog)/N))
    prog=prog+1
    # get the url content
    content=run_function_with_done_print(requests.get, "Getting content from {}...".format(url), (url,))
    dataset=run_function_with_done_print(dat_to_netcdf, "Converting to NetCDF...", (content.text,args.destination, args.brief,))
  
