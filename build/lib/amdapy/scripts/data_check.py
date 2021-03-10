## Script for checking the integrity of AMDA virtual instrument data files.
#
#  @file data_check.py
#  @author Alexandre Schulz
#  @brief Take a NetCDF file as input (or zipped file) 
import os
import argparse
import numpy as np

from netCDF4 import Dataset
from amdapy.ddtime import DDTime

## check_required_parameters(dataset)
#
#  Check that the dataset contains the required parameters.
#  @param dataset dataset object we wish to check.
#  @return bool True if dataset contains all required parameters, False otherwise.
def check_required_parameters(dataset):
  required_parameters=["Time", "StartTime", "StopTime"]
  for p in dataset.variables:
    if p in required_parameters:
      required_parameters.remove(p)
      if len(required_parameters)==0:
        return True
  return False
## parse_args
#
#  Parse command line arguments.
def parse_args():
  parser=argparse.ArgumentParser()
  parser.add_argument("input", help="input NetCDF file", type=str)
  return parser.parse_args()
if __name__=="__main__":
  args=parse_args()
  # open dataset
  dataset=Dataset(args.input, mode="r", format="NETCDF3_CLASSIC")
  # check that the dataset contains the following three parameters
  if not check_required_parameters(dataset):
    print("File is missing required parameters")
    exit()
  # get StartTime
  st=np.array(dataset.variables["StartTime"])
  et=np.array(dataset.variables["StopTime"])
  t=np.array(dataset.variables["Time"])
  st_str="".join([k.decode("UTF-8") for k in st])
  et_str="".join([k.decode("UTF-8") for k in et])
  print("StartTime : {}".format(st_str))
  print("StopTime  : {}".format(et_str))

  ddt0=DDTime.from_utctimestamp(t[0])
  ddt1=DDTime.from_utctimestamp(t[-1])
  print("Time 0 to DDTIME : {} {}".format(ddt0, len(ddt0)))
  print("Time -1 to DDTIME : {} {}".format(ddt1, len(ddt1)))
  mods={}
  if ddt0!=st_str:
    print("Setting new StartTime : {}".format(ddt0))
    mods["StartTime"]=[k for k in ddt0]
  if ddt1!=et_str:
    print("Setting new StopTime : {}".format(ddt1))
    mods["StopTime"]=[k for k in ddt1]
  
  if len(mods):
    new_d=Dataset("temp.nc", mode="w", format="NETCDF3_CLASSIC")
    for d in dataset.dimensions:
      dname=d
      dsize=dataset.dimensions[d].size
      if dname=="Time":
        dsize=None
      new_d.createDimension(dname,dsize)
    for v in dataset.variables:
      var=dataset.variables[v]
      vname=var.name
      vdtype=var.datatype
      vdims=var.dimensions
      vardata=None
      if v in mods:
        vardata=mods[v]
      else:
        vardata=var[:]
      new_d.createVariable(v, vdtype, vdims)
      print("Created variable : {} {} {}".format(v, vdtype, vdims))
      if isinstance(vardata, list):
        print(len(vardata))
        if len(vardata)==16:
          print("wrong len vardata : {}".format(vardata))
          vardata=vardata+["\0"]
      else:
        print(vardata.shape)
      new_d.variables[v][:]=vardata
    new_d.sync()
    new_d.close()
    filename=args.input.split("/")[-1]
    filedir="/".join(args.input.split("/")[:-1])
    brief=filename.split("_")[0]
    print("rm {}".format(args.input))
    os.system("rm {}".format(args.input))
    datt=ddt0[:16].replace("\0","")
    os.system("mv temp.nc {}/{}_{}.nc".format(filedir,brief, datt))
  dataset.close()
