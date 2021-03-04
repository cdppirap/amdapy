"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: dataset.py
:brief: Base classes and functions for manipulating dataset objects.

"""
import numpy as np
from amdapy.core.variable import Variable

class Dataset:
  """Dataset base class. We use this class for representing dataset objects. Dataset are a collection
  of variables, often stored in a file, but can exist only in memory. This is the base class from
  which we derive all other dataset. In particular this call will be subclassed to provide interfaces
  to the various file formats we can encounter during our work.
  """
  def __init__(self, dataset_id, variables=[]):
    """Dataset initialization
    :param dataset_id: dataset identification, should be unique withing the context of a dataset 
    provider.
    :type dataset_id: string
    :param variables: list of variables belonging to the dataset
    :type variables: list of amdapy.core.Variable objects.
    """
    self.id=dataset_id
    self.variables=variables
  def contains(self, var):
    """Check if the current dataset contains a variable
    :param var: variable object
    :type var: amdapy.core.Variable
    :return: bool
    """
    for v in self.variables:
      if v==var:
        return True
    return False
  def __str__(self):
    """Dataset string representation
    """
    return "Dataset(id:{},n_var:{})".format(self.id,len(self.variables))

if __name__=="__main__":
  print("Testing amdapy.core.Dataset implementation")
  dataset=Dataset("dataset1", [Variable(str(k),np.float64, data=np.ones(2)) for k in range(3)])
  print(dataset)
  for v in dataset.variables:
    print(v)
