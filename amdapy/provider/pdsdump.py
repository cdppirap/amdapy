"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: pdsdump.py
:brief: Use this script to convert a dataset from PDS ASCII format to NetCDF

Usage : --dump : print contents of the dataset
        --convert2netcdf : convert file to NetCDF
        -o, --output : output filename
"""

import sys
import datetime
import numpy as np
import os
import argparse
from netCDF4 import Dataset

from amdapy.pds import PDSDataset
from amdapy.str_utils import str_is_integer
from amdapy.ddtime import DDTime

def parse_args():
  """Parse command line arguments
  
  :return: command line arguments
  :rtype: argparse.Arguments
  """
  parser=argparse.ArgumentParser()
  parser.add_argument("input",help="input file",type=str)

  # optional arguments
  parser.add_argument("--dump",help="dump dataset contents",action="store_true")
  parser.add_argument("-o","--output",help= "output filename",type=str,default=None)
  parser.add_argument("--convert2netcdf",help="convert file to NetCDF format",action="store_true")
  parser.add_argument("--namemap",help="map old column name to new name",type=str)
  parser.add_argument("--separator", help="separation character for the table file", type=str, default=" ")
  parser.add_argument("--brief", help="output file prefix", type=str, default="dataset")
  args=parser.parse_args()
  return args

def parse_namemap_hint(hint_str):
  """Parse the namemap hint

  :param hint_str: string indicating the correspondance between old and new column names
  :type hint_str: str
  :return: dictionary mapping new column names with the old column names
  :rtype: dict
  """
  if hint_str is None:
    return {}
  a={k.split(":")[0]:k.split(":")[1] for k in hint_str.split(";")}
  for k in a:
    if "," in a[k]:
      a[k]=a[k].split(",")
  return a

def get_column_name_mapping(data, hint=None):
  """Get mapping of new column name to old columns

  :param data: input data object
  :type data: amdapy.pds.PDSDataset
  :return: dictionary mapping old dataset column name with onew column names
  :rtype: dict
  """
  ans={}
  if hint is None:
    for c in data.column_names():
      dt=data.column_datatype(c)
      n_name=c.replace(" ","_").replace("\"","").upper()
      if dt=="TIME":
        ans["Time"]=c
    return ans
  else:
    hint_map=parse_namemap_hint(hint)
    return hint_map
def pds_to_netcdf(data, output=None, namemap=None,prefix=None):
  """Convert a PDS ASCII dataset to NetCDF

  :param data: PDSDataset object handler
  :type data: amdapy.pds.PDSDataset
  :param output: output filename, optional
  :type output: str
  :param namemap: dictionary mapping new column name to old column names
  :type namemap: dict
  :param prefix: prefix to apply to all datafiles, optional
  :type prefix: str
  """
  filename="nc_dataset.nc"
  dimensions={"Time":None, "TimeLength":17}
  mapping={}
  start_t,stop_t=data.timespan()
  start_dt,stop_dt=datetime.datetime.utcfromtimestamp(start_t),datetime.datetime.utcfromtimestamp(stop_t)
  start_str,stop_str=DDTime.from_datetime(start_dt),DDTime.from_datetime(stop_dt)
  variables={"StartTime":("TimeLength","c",start_str),"StopTime":("TimeLength","c",stop_str)}
  if not namemap is None:
    for c in namemap:
      if isinstance(namemap[c],list):
        temp_dim=len(namemap[c])
        # check if the mapping contains a dimension of the right size, if not then create one
        n_dim=""
        for d in dimensions:
          if dimensions[d]==temp_dim:
            n_dim=d
        if n_dim=="":
          i=0
          n_dim="dim{}".format(i)
          while n_dim in dimensions:
            i=i+1
            n_dim="dim{}".format(i)
          dimensions[n_dim]=temp_dim
        temp_data=[]
        for or_cc in namemap[c]:
          col_name=or_cc
          if (not data.has_column(or_cc)) and str_is_integer(or_cc):
            col_name=data.column_name_by_index(int(or_cc))
          col_data=data.column_data(col_name)
          dt=data.column_datatype(col_name)
          temp_data.append(col_data)
        temp_data=np.array(temp_data).T
        variables[c]=(("Time",n_dim),dt,temp_data)
          
      else:
        orig_colname=namemap[c]
        if not data.has_column(orig_colname) and str_is_integer(orig_colname):
          orig_colname=data.column_name_by_index(int(orig_colname))
        col_data=data.column_data(orig_colname)
        col_shape=col_data.shape
        if len(col_shape)==2:
          # find the value of the second dimension 
          second_dim_value=col_shape[1]
          # search for dimension in the netcdf file that has the same value, if none exist then add one
          n_dim=""
          for dim in dimensions:
            if dimensions[dim]==second_dim_value:
              n_dim=dim
          if n_dim=="":
            i=0
            n_dim="dim{}".format(i)
            while n_dim in dimensions:
              i=i+1
              n_dim="dim{}".format(i)
            dimensions[n_dim]=second_dim_value
            col_datatype=data.column_datatype(orig_colname)
            variables[c]=(("Time",n_dim),col_datatype, col_data)
        else:
          col_datatype=data.column_datatype(orig_colname)
          variables[c]=("Time", col_datatype,col_data)
    if not prefix is None:
      filename="{}_{}.nc".format(prefix,start_str[:-1])
    else:
      filename="dataset_{}.nc".format(start_str[:-1])
    nc_dataset=Dataset(filename,mode="w",format="NETCDF3_CLASSIC")
    for d in dimensions:
      dim_nam,dim_size=d,dimensions[d] 
      nc_dataset.createDimension(dim_nam,size=dim_size)

    for v in variables:
      var_name=v
      var_dim, var_dt, var_data=variables[v]
      if var_dt == "TIME":
        var_dt=np.float64
      nc_dataset.createVariable(var_name, var_dt, dimensions=var_dim)
      nc_dataset.variables[var_name][:]=var_data
    nc_dataset.sync()

if __name__=="__main__":
  args=parse_args()
  
  if not args.input:
    print("arguments are wrong")
    print("should print help here ")
    exit()
  
  label_filename=args.input+".LBL"
  data_filename=args.input+".TAB"
  
  if not os.path.exists(label_filename):
    print("Label file does not exist : {}".format(label_filename))
    exit()
  if not os.path.exists(data_filename):
    print("Data file does not exist : {}".format(data_filename))

  # initialize dataset
  data=PDSDataset(label_filename=label_filename, data_filename=data_filename, table_sep=args.separator)
  if args.dump:
    data.summary()
    exit()

  if args.convert2netcdf:
    output_filename=args.input+".nc"
    print("converting file to netcdf : {}".format(output_filename))
    # map old column name to new names if they are given
    if args.namemap:
      print("\tuser defined column name mapping")
    else:
      print("\tdefault name mapping")
    namemap=get_column_name_mapping(data,hint=args.namemap)
    pds_to_netcdf(data, output=output_filename,namemap=namemap, prefix=args.brief)
