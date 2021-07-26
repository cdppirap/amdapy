"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: dataset.py
:brief: Base classes and functions for manipulating dataset objects.

Base class for representing datasets. Provides access to the data and variables names etc.

"""
import numpy as np
from amdapy.core.parameter import Parameter
from amdapy.core.variable import Variable

class Dataset:
  """AMDA dataset container. Retrieving data from AMDA can be time consuming, as such
  the object constructor can be called without setting the data. 

  :param el: dataset unique identificator
  :type el: amdapy.rest.client.DatasetElement
  :param data: optional (default: None), dataset content 
  :type data: array type
  
  Get list of parameter ids : 

  .. code-block:: python 

     >>> [p.id for p in dataset.iter_parameter()]
     ['ura_sw_n', 'ura_sw_v', 'ura_sw_t', 'ura_sw_pdyn', 'ura_sw_b', 'ura_sw_bx', 'ura_sw_da']

  You can then get the contents of the parameters by using the bracket operator : 

  .. code-block:: python

     >>> dataset["ura_sw_n"]
  """
  def __init__(self, el, data):
    """Object constructor
    """
    self.id=el.id
    self.el=el
    self.data=data
    self.globalstart=self.data.index[0]
    self.globalstop=self.data.index[-1]
    self.parameters=[]
    self.make_parameter_list(el)
  def make_parameter_list(self, el):
    for p in el.parameters:
      param=Parameter(p.id, p.name, p.units, None)
      if p.n==1:
        param.data=self.data[p.name]
      else:
        # get the names of the columns
        cc=[]
        for c in p.components:
          cc.append(p.name+"_"+c.name)
        param.data=self.data[cc]
      self.parameters.append(param)
        
  def iter_parameter(self):
    """Parameter iterator

    :return: parameter object
    :rtype: amdapy.amda.Parameter

    Parameter iterator. For example get a list of parameter name and units :

    .. code-block:: python

       >>> [p.name for p in dataset.iter_parameter()]
       ['density', 'velocity', 'temperature', 'dynamic pressure', 'b tangential', 'b radial', 'angle Uranus-Sun-Earth']
       >>> [p.units for p in dataset.iter_parameter()]
       ['cm⁻³', 'km/s', 'eV', 'nPa', 'nT', 'nT', 'deg']

    """
    for p in self.parameters:
      yield p
  def __str__(self, show_params=True):
    """Dataset string representation

    :param show_params: optional (default: True), print parameters also
    :type show_params: bool
    :return: dataset string representation
    :rtype: str
    """
    a="Dataset (id:{}, start:{}, stop:{}, n_param:{})".format(self.id, self.globalstart, self.globalstop,len(self.el.parameters))
    for p in self.parameters:
      a="{}\n\t{}".format(a,p)
    return a
  def time(self):
    """Get time value for this dataset

    :return: time 
    :rtype: pandas.DataFrame 

    Get the datasets time values.

    .. code-block:: python

       >>> T = dataset.time()
       >>> type(T)
       <class 'pandas.core.indexes.datetimes.DatetimeIndex'>
       >>> T
       DatetimeIndex(['2010-01-01 01:00:00', '2010-01-01 02:00:00',
                      '2010-01-01 03:00:00', '2010-01-01 04:00:00',
       ...
                      '2010-01-01 23:00:00', '2010-01-02 00:00:00'],
                     dtype='datetime64[ns]', name='Time', freq=None)

    """
    return self.data.index
  def __getitem__(self,key):
    """Item getter

    :param: item key, either parameter id or name
    :type key: check numpy documentation
    :return: desired items
    :rtype: check numpy documentation for an answer
    """
    if isinstance(key, slice):
      return self.data[key]
    if isinstance(key, str):
      # check parameter names and ids      
      for v in self.parameters:
        if v.id==key or v.name==key:
          return v
      # check if it corresponds to a column
      if key in self.data.columns:
          return self.data[key]

#class Dataset:
#  """Dataset base class. We use this class for representing dataset objects. Dataset are a collection
#  of variables, often stored in a file, but can exist only in memory. This is the base class from
#  which we derive all other dataset. In particular this call will be subclassed to provide interfaces
#  to the various file formats we can encounter during our work.
#  
#  :param dataset_id: dataset identification string, should be unique.
#  :type dataset_id: str
#  :param variables: list of variables contained in the dataset, optional
#  :type param: list of :class:`amdapy.core.variable.Variable` objects
#  """
#  def __init__(self, dataset_id, variables=[]):
#    """Constructor
#    """
#    self.id=dataset_id
#    self.variables=variables
#  def contains(self, var):
#    """Check if the current dataset contains a variable
#
#    :param var: variable object
#    :type var: amdapy.core.Variable
#    :return: True if dataset contains variable, False otherwise
#    :rtype: bool
#    """
#    for v in self.variables:
#      if v==var:
#        return True
#    return False
#  def iter_variable(self):
#    """Variable iterator
#
#    :return: variable
#    :rtype: amdapy.core.variable.Variable
#    """
#  def __str__(self):
#    """Dataset string representation
#
#    :return: string representation of the dataset object.
#    :rtype: str
#    """
#    return "Dataset(id:{},n_var:{})".format(self.id,len(self.variables))
#
#if __name__=="__main__":
#  print("Testing amdapy.core.Dataset implementation")
#  dataset=Dataset("dataset1", [Variable(str(k),np.float64, data=np.ones(2)) for k in range(3)])
#  print(dataset)
#  for v in dataset.variables:
#    print(v)
