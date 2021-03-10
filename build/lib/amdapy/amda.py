"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: AMDA dataset provider


"""
import amdapy
import datetime
from amdapy.core.dataset import Dataset
from amdapy.core.provider import DataProvider
from amdapy.amdaWSClient.client import get_obs_tree

class AMDADataset(Dataset):
  """AMDA dataset container. Retrieving data from AMDA can be time consuming, as such
  the object constructor can be called without setting the data. 

  :param el: dataset unique identificator
  :type el: amdapy.amdaWSClient.client.DatasetElement
  :param get_data: optional (default: False), get the dataset contents at initialization
  :type get_data: bool

  """
  def __init__(self, el, get_data=False):
    """Object constructor
    """
    super().__init__(el.id)
    self.el=el
    try:
      self.starttime=datetime.datetime.strptime(self.el.datastart, amdapy.amdaWSClient.obstree.DATE_FORMAT)
      self.stoptime=datetime.datetime.strptime(self.el.datastop, amdapy.amdaWSClient.obstree.DATE_FORMAT)
    except:
      self.starttime=None
      self.stoptime=None
    if get_data:
      self.get()
  def iter_variable(self):
      for p in self.el.parameters:
          yield p
  def __str__(self):
    """Dataset string representation

    :return: dataset string representation
    :rtype: str
    """
    a="AMDADataset(id:{}, start:{}, stop:{}, n_param:{})".format(self.id, self.starttime, self.stoptime,len(self.el.parameters))
    return a
  def get(self, timedelta=datetime.timedelta(hours=1)):
    """Get the dataset contents. Can be time consuming, default behavior is to only retrieve
    the first hour of data

    :param timedelta: optional, default is datetime.timedelta(hours=1)
    :type timedelta: datetime.timedelta
    """
    dt_format="%Y-%m-%dT%H:%M:%SZ"
    d0=datetime.datetime.strptime(self.el.datastart, dt_format)
    #d1=datetime.datetime.strptime(self.el.datastop, dt_format)
    d1=d0+datetime.timedelta(hours=1)
    #x=amdapy.amdaWSClient.client.get_dataset(self.id, d0,d1)
    for parameter in self.el.parameters:
      psize=parameter.component_count()
      col_names=None
      if psize==0:
        col_names=[parameter.id]
      else:
        col_names=[parameter.id+str(k) for k in range(psize)]
      col_names=["Time"]+col_names
      y=amdapy.amdaWSClient.client.get_parameter(parameter.id, d0, d1, col_names)
      self.variables.append(amdapy.core.variable.Variable(name=parameter.id, dtype=None, value=y))

class AMDA(DataProvider):
  """Class for accessing data on AMDA
  """
  def __init__(self):
    """Object constructor
    """
    super().__init__(name="AMDA")
    self.tree=get_obs_tree()
  def iter_dataset(self, mission=None, instrument=None):
    """Dataset iterator

    :return: AMDA dataset
    :rtype: amdapy.amda.AMDADataset
    """
    for datasetel in self.tree.iter_dataset(mission=mission, instrument=instrument):
      yield self.datasetel_to_dataset(datasetel)
  def datasetel_to_dataset(self, datasetel):
    """Convert a :class:`amdapy.amdaWSClient.obstree.DatasetElement` object to a :class:`amdapy.amda.AMDADataset` object

    :param datasetel: dataset representation
    :type datasetel: amdapy.amdaWSClient.obstree.DatasetElement
    :return: dataset representation
    :rtype: amdapy.amda.AMDADataset

    """
    return AMDADataset(datasetel)
  def get_dataset(self, dataset_id, get_data=False):
    """Get dataset by id

    :param dataset_id: dataset id
    :type dataset_id: str
    :param get_data: flag indicating if datasets content should be retrieved at initialization
    :type get_data: bool
    :return: dataset object if found, None otherwise
    :rtype: amdapy.amda.AMDADataset or None
    """
    for d in self.iter_dataset():
      if d.id==dataset_id:
        if get_data:
          d.get()
        return d
    return None
  def missions(self):
    """Get list of missions

    :return: List of mission names
    :rtype: list
    """
    return [m for m in self.tree.iter_mission()]
  def instruments(self, mission):
    """Get list of instrument names

    :param mission: mission name
    :type mission: str
    :return: list of instrument names
    :rtype: str
    """
    mission=self.tree.find_mission(mission)
    return [i for i in mission.instruments]


if __name__=="__main__":
  print("AMDA provider")
  amda=AMDA()
  for dataset in amda.iter_dataset():
    print(dataset)

  dataset_id="ace-imf-all"
  dataset = amda.get_dataset(dataset_id)
  print([var.name for var in dataset.variables])
  dataset.get()
  print([var.name for var in dataset.variables])
  for var in dataset.variables:
    print(type(var))
  
  print("Getting dataset with data")
  dataset2=amda.get_dataset(dataset_id,get_data=True)
  print("data type : {}".format(type(dataset2.variables[0])))
  print(dataset2.variables[0][:])
  var=dataset2.variables[0]
  print(type(var[:]))

  print("Mission list")
  print([m.name for m in amda.missions()])

  print("Instrument list for ACE mission")
  print([i.name for i in amda.instruments("ACE")])

  print("Datasets belonging to ACE/ MFI")
  for d in amda.iter_dataset(mission="ACE", instrument="MFI"):
      print(d)

  print("Iterate over parameters of the dataset")
  for var in dataset2.iter_variable():
      print(var.name, var.units)
