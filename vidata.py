"""
:author: Alexandre Schulz
:file: vidata.py
:brief: Utlities for managing the Virtual Instrument datafiles
"""

"""Required dimensions
"""
required_dimensions=[NetCDFDim("Time",None), NetCDFDim("TimeLength",17)]
"""Required variables
"""
required_variables=[NetCDFVar("Time",np.float64,("Time")), \
                    NetCDFVar("StartTime", "c", ("TimeLength")), \
                    NetCDFVar("StopTime", "c", ("TimeLength"))]

class NetCDFDim:
  def __init__(self, dimname, size):
    self.name=dimname
    self.size=size
  def add_to_netcdf_dataset(self, dataset):
    dataset.createDimension(self.name, self.size)
class NetCDFVar:
  def __init__(self, varname, datatype, dimensions, data=None):
    self.name=varname
    self.datatype=datatype
    self.dimensions=dimensions
    self.data=data
  def add_to_netcdf_dataset(self, dataset):
    dataset.createVariable(self.name, self.datatype, self.dimensions)
    if not self.data is None:
      dataset.variables[self.name][:]=self.data

class VIDatasetGenerator:
  def __init__(self, path):
    self.path=path
  def get_time_seconds(self, arr):
    # check the type of the date objects
    t=arr[:,0]
    if type(t[0])==datetime.datetime:
      return np.array([dt_to_seconds(k) for k in t])
    return t
  def create_from_array(self,filename, arr, ud_dimensions, ud_variables):
    dataset=Dataset(filename, mode="w", format="NETCDF3_CLASSIC")
    # add the required dimensions
    for dim in required_dimensions:
      dim.add_to_netcdf_dataset(dataset)
    # add the required variables
    for var in required_variables:
      var.add_to_netcdf_dataset(dataset)
    # get the user defined variables
    for dim in ud_dimensions:
      dim.add_to_netcdf_dataset(dataset)
    for var in ud_variables:
      var.add_to_netcdf_dataset(dataset)
    # set time data
    dataset.variables["Time"][:]=self.get_time_seconds(arr)
    # set StartTime
    sddt=DDTime.from_datetime(arr[0,0])
    dataset.variables["StartTime"][:]=sddt
    stddt=DDTime.from_datetime(arr[-1,0])
    dataset.variables["StopTime"][:]=stddt
    dataset.sync()
      
