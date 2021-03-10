"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: dataset.py
:brief: Base classes and functions for manipulating dataset objects.

Base class for representing datasets. Provides access to the data and variables names etc.

"""
import numpy as np
from amdapy.core.variable import Variable

class Dataset:
  """Dataset base class. We use this class for representing dataset objects. Dataset are a collection
  of variables, often stored in a file, but can exist only in memory. This is the base class from
  which we derive all other dataset. In particular this call will be subclassed to provide interfaces
  to the various file formats we can encounter during our work.
  
  :param dataset_id: dataset identification string, should be unique.
  :type dataset_id: str
  :param variables: list of variables contained in the dataset, optional
  :type param: list of :class:`amdapy.core.variable.Variable` objects
  """
  def __init__(self, dataset_id, variables=[]):
    """Constructor
    """
    self.id=dataset_id
    self.variables=variables
  def contains(self, var):
    """Check if the current dataset contains a variable

    :param var: variable object
    :type var: amdapy.core.Variable
    :return: True if dataset contains variable, False otherwise
    :rtype: bool
    """
    for v in self.variables:
      if v==var:
        return True
    return False
  def iter_variable(self):
    """Variable iterator

    :return: variable
    :rtype: amdapy.core.variable.Variable
    """
  def __str__(self):
    """Dataset string representation

    :return: string representation of the dataset object.
    :rtype: str
    """
    return "Dataset(id:{},n_var:{})".format(self.id,len(self.variables))

if __name__=="__main__":
  print("Testing amdapy.core.Dataset implementation")
  dataset=Dataset("dataset1", [Variable(str(k),np.float64, data=np.ones(2)) for k in range(3)])
  print(dataset)
  for v in dataset.variables:
    print(v)
