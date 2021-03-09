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

  """
  def __init__(self, el):
    """Object constructor
    """
    super().__init__(el.id)
    self.el=el
  def __str__(self):
    """Dataset string representation

    :return: dataset string representation
    :rtype: str
    """
    return "AMDADataset(id:{})".format(self.id)
  def get(self):
    """Get the dataset contents. Can be time consuming.
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
  def iter_dataset(self):
    for datasetel in self.tree.iter_dataset():
      yield self.datasetel_to_dataset(datasetel)
  def datasetel_to_dataset(self, datasetel):
    return AMDADataset(datasetel)
  def get_dataset(self, dataset_id):
    for d in self.iter_dataset():
      if d.id==dataset_id:
        return d
    return None


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

