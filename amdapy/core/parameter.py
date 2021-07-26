"""Base Parameter class
"""

import matplotlib.pyplot as plt

class Parameter:
  """Container class for storing parameter objects.

  :param id: identifier of the parameter, should be unique 
  :type id: str
  :param name: name of the parameter as seen in the AMDA navigation tree
  :type name: str
  :param units: units in which are expressed the parameters values
  :type units: str
  :param data: values of the parameter
  :type data: pandas.DataFrame

  This class is a container for parameter data including identification, name, units and data. We 
  retrieve :class:`amdapy.amda.Parameter` instances by passing a :class:`amdapy.amda.Collection.Parameter`
  object to the :meth:`amdapy.amda.AMDA.get` or :meth:`amdapy.amda.AMDA.get_dataset` method.

  .. code-block:: python

     >>> parameter
     Parameter (id:ura_sw_n, name:density, units:cm⁻³, shape: (24, 1))

  """
  def __init__(self,id, name, units, data):
    """Object constructor
    """
    self.id=id
    self.name=name
    self.units=units
    self.data=data
  def plot(self, dataset_id=None, figsize=None):
    """Plot the parameter. Naive plotting function for visualizing time series data.

    :return: pyplot figure object
    :rtype: pyplot figure
    """
    fig=plt.figure(figsize=figsize)
    if dataset_id is None:
      plt.title("param: {}".format(self.name))
    else:
      plt.title("dataset: {}, param: {}".format(dataset_id, self.name))
    # check if parameter has multiple components
    if len(self.data.shape)>1:
      for i in range(self.data.shape[1]):
        plt.plot(self.data.iloc[:,i],label=self.data.columns[i].replace(self.name, ""))
      plt.legend([self.data.columns[i] for i in range(self.data.shape[1])])  
    else:
      plt.plot(self[:])
    plt.xlabel("Time")
    plt.grid(True)
    plt.ylabel("{} ({})".format(self.name, self.units))
    fig.autofmt_xdate()
    plt.show()
    return 
  def __getitem__(self, key):
    """Get parameter data
    
    :param key: key, this argument is passed directly to the :data:`data.__getitem__` methode.
    :type key: slice
    :return: desired parameter data
    :rtype: pandas.DataFrame
    """
    return self.data[key]
  def __str__(self):
    """String representation of the current parameter object

    :return: string representation of the current object
    :rtype: str
    """
    if self.data is None:
      return "Parameter (id:{}, name:{}, units:{}, nodata)".format(self.id, self.name, self.units)
    return "Parameter (id:{}, name:{}, units:{}, shape: {})".format(self.id, self.name, self.units, self.data.shape)


"""Base class for containing user parameter descriptions
"""
class DerivedParameter:
    def __init__(self, userid, paramid, name, timestep, buildchain, attrib={}):
        self.userid=userid
        self.paramid=paramid
        self.name=name
        self.timestep=timestep
        self.buildchain=buildchain
        self.attrib=attrib
    def __str__(self):
        return "DerivedParameter (user={}, id={}, name={})".format(self.userid, self.parameter_id(), self.name)
    def parameter_id(self):
        return "ws_{}".format(self.name)
    @staticmethod
    def from_tree_element(el, userid):
        did=""
        name=el.attrib["name"]
        buildchain=el.attrib["buildchain"]
        timestep=float(el.attrib["timestep"])

        for k in el.attrib:
            if k.endswith("}id"):
                did=el.attrib[k]
        return DerivedParameter(userid, did, name, timestep, buildchain, el.attrib)
   
