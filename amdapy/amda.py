"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: AMDA dataset provider

:class:`amdapy.amda.AMDA` is the object through witch we can query the AMDA database for 
available missions, instruments and datasets. Datasets are stored following a predefined
hierarchy::

    AMDA collection 
        Mission A
            Instrument X
                Dataset 1
                ...
                Dataset N
            ...
        ...



"""
import amdapy
import datetime
import pandas as pd
from amdapy.amdaWSClient.client import get_obs_tree

class Timespan:
  """Time interval container class

  :param start: start date time
  :type start: datetime.datetime or None
  :param stop: stop date time
  :type stop: datetime.datetime
  """
  def __init__(self, start, stop):
    """Object constructor
    """
    self.start=start
    self.stop=stop
  def __contains__(self, o):
    """Check if timespan contains another object

    :param o: object to check, can be a datetime object or a Timespan
    :type o: datetime.datetime or Timespan
    :return: True if current timespan object contains :data:`o`
    :rtype: True or False
    """
    if isinstance(o, datetime.datetime):
      return self.start <= o and self.stop > o
    if isinstance(o, Timespan):
      return self.start <= o.start and self.stop > o.stop
    return False

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
class Dataset:
  """AMDA dataset container. Retrieving data from AMDA can be time consuming, as such
  the object constructor can be called without setting the data. 

  :param el: dataset unique identificator
  :type el: amdapy.amdaWSClient.client.DatasetElement
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
    self.starttime=el.starttime
    self.stoptime=el.stoptime
    self.data=data
    self.parameters=[]
    self.make_parameter_list(el)
  def make_parameter_list(self, el):
    for p in el.parameters:
      param=Parameter(p.id, p.name, p.units, None)
      if p.n==1:
        param.data=self.data[p.name]
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
    a="Dataset (id:{}, start:{}, stop:{}, n_param:{})".format(self.id, self.starttime, self.stoptime,len(self.el.parameters))
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
class AMDA:
  """Class for accessing data on AMDA
  """
  def __init__(self):
    """Object constructor
    """
    self.name="AMDA"
    self.collection=Collection()
  def datasetel_to_dataset(self, datasetel, t_interval):
    """Convert a :class:`amdapy.amdaWSClient.obstree.DatasetElement` object to a :class:`amdapy.amda.AMDADataset` object

    :param datasetel: dataset representation
    :type datasetel: amdapy.amdaWSClient.obstree.DatasetElement
    :param t_interval: time interval for which we want the dataset data
    :type t_interval: Timespan
    :return: dataset representation
    :rtype: amdapy.amda.AMDADataset

    """
    # get the data
    cols=self.get_column_names(datasetel)
    did=datasetel.id
    if t_interval is None:
      startt=datasetel.starttime
      stopt=startt+datetime.timedelta(days=1)
    else:
      startt=t_interval.start
      stopt=t_interval.stop
    data=amdapy.amdaWSClient.client.get_dataset(did, startt, stopt, cols)
    data.columns=cols
    data["Time"]=pd.to_datetime(data["Time"])
    data.set_index("Time",inplace=True)
    return Dataset(datasetel, data=data)
  def get_column_names(self, datasetel):
    """Get list of column names

    :param datasetel: dataset collection item
    :type datasetel: amdapy.amda.Collection
    :return: list of the column names
    :rtype: list of str
    """
    # the dataset contains Time as first column
    col=["Time"]
    # check each parameter
    for p in datasetel.parameters:
      if p.n>1:
        for c in p.components:
          col.append("{}_{}".format(p.name,c.name))
      else:
        col.append(p.name)
    return col

  def get(self, item, t_interval=None):
    """Gets a item from the collection.

    :param item: collection item
    :type item: amdapy.amda.CollectionItem
    :param t_interval: time interval, if this is None then return only the **first day** of data
    :type t_interval: Timespan
    :return: parameter or dataset depending on the input, None if item is badly defined
    :rtype: amda.Parameter or amda.Dataset
    
    The behaviour of this method depends on the type of the :data:`item` argument : 
      * :class:`amdapy.amda.Collection.Dataset` then call the :meth:`amdapy.amda.AMDA.get_dataset`
      * :class:`amdapy.amda.Collection.Parameter` then call the :meth:`amdapy.amda.AMDA.get_parameter`

    For example retriving the *tao-ura-sw* dataset is done like this : 

    .. code-block:: python

      >>> dataset_desc = amda.find("tao-ura-sw")
      >>> data = amda.get(dataset_desc)
      >>> data
      Dataset (id:tao-ura-sw, start:2010-01-01 00:00:00, stop:2021-02-19 00:00:00, n_param:7)
          Parameter (id:ura_sw_n, name:density, units:cm⁻³, value: None)
          Parameter (id:ura_sw_v, name:velocity, units:km/s, value: None)
          Parameter (id:ura_sw_t, name:temperature, units:eV, value: None)
          Parameter (id:ura_sw_pdyn, name:dynamic pressure, units:nPa, value: None)
          Parameter (id:ura_sw_b, name:b tangential, units:nT, value: None)
          Parameter (id:ura_sw_bx, name:b radial, units:nT, value: None)
          Parameter (id:ura_sw_da, name:angle Uranus-Sun-Earth, units:deg, value: None)

    """
    if isinstance(item, Collection.Dataset):
      return self.get_dataset(item, t_interval)
    elif isinstance(item, Collection.Parameter):
      return self.get_parameter(item)
    else:
      print("Getting other")
  def get_parameter(self, param, t_interval=None):
    """Get parameter data.

    :param param: parameter descriptor
    :type param: amda.Collection.Parameter 
    :param t_interval: time interval, optional, default is None in which case only the first day of data is produced
    :type t_interval: Timespan
    :return: Parameter object
    :rtype: amdapy.amda.Parameter

    Given a valid :class:`amdapy.amda.Collection.Parameter` instance you can retrieve the parameters 
    data by calling the :meth:`amdapy.amda.AMDA.get_parameter` method on the desired time interval.

    If the time interval provided is not valid then only the first day of data will be returned. Data
    is stored as a :class:`pandas.DataFrame` object indexed by time (since all AMDA parameters are
    timeseries), and you can access it through the :data:`data` attribute.

    Continuing with the example dataset :data:`tao-ura-sw` you can retrive the *density* parameter (id : ura_sw_n) like this : 

    .. code-block:: python

        >>> parameter_desc = amda.collection.find("ura_sw_n")
        >>> parameter_desc
        Parameter item (id:ura_sw_n, name:density, units:cm⁻³, disp:None, dataset:tao-ura-sw, n:1)
        >>> parameter = amda.get_parameter(parameter_desc)
        >>> parameter
        Parameter (id:ura_sw_n, name:density, units:cm⁻³, shape: (24, 1))
        >>> parameter_desc[:]
                             density
        Time                        
        2010-01-01 01:00:00    0.005
        2010-01-01 02:00:00    0.006
        ...
        2010-01-01 23:00:00    0.008
        2010-01-02 00:00:00    0.008

    """
    psize=param.n
    col_names=None
    if psize==1:
      col_names=[param.name]
    else:
      col_names=[param.name+"_"+str(k.name) for k in param.components]
    col_names=["Time"]+col_names
    if t_interval is None:
      # get the parent dataset description
      parent_desc=self.collection.find(param.dataset_id)
      startt=parent_desc.starttime
      stopt=startt+datetime.timedelta(days=1)
    else:
      startt=t_interval.start
      stopt=t_interval.stop
    d=amdapy.amdaWSClient.client.get_parameter(param.id, startt,stopt, col_names)
    d.set_index("Time", inplace=True)
    return Parameter(id=param.id, name=param.name, data=d,units=param.units)
  def get_dataset(self, dataset_item, t_interval=None):
    """Get dataset contents.

    :param dataset_item: dataset item
    :type dataset_id: Collection.Dataset
    :param t_interval: time interval, if None is passed then only return the first hour of data
    :type t_interval: Timespan or None
    :return: dataset object if found, None otherwise
    :rtype: amdapy.amda.Dataset or None

    Retrieves the dataset contents between :data:`t_interval.start` to :data:`t_interval.stop`. If the
    :data:`t_interval` is not a valid interval then only the first day of data will be retrieved. This
    behaviour was chosen to avoid too many requests for downloading the whole dataset (which can be
    extensive).

    In the following example we download the first day of the :data:`tao-ura-sw`.

    .. code-block:: python

       >>> amda = AMDA()
       >>> dataset_desc = amda.collection.find("tao-ura-sw")
       >>> dataset = amda.get_dataset(dataset_desc)
       >>> dataset
       Dataset (id:tao-ura-sw, start:2010-01-01 00:00:00, stop:2021-02-19 00:00:00, n_param:7)
           Parameter (id:ura_sw_n, name:density, units:cm⁻³, shape: (24,))
           Parameter (id:ura_sw_v, name:velocity, units:km/s, nodata)
           Parameter (id:ura_sw_t, name:temperature, units:eV, shape: (24,))
           Parameter (id:ura_sw_pdyn, name:dynamic pressure, units:nPa, shape: (24,))
           Parameter (id:ura_sw_b, name:b tangential, units:nT, shape: (24,))
           Parameter (id:ura_sw_bx, name:b radial, units:nT, shape: (24,))
           Parameter (id:ura_sw_da, name:angle Uranus-Sun-Earth, units:deg, shape: (24,))

    The actual data is stored as a :class:`pandas.DataFrame` object. You can access the data
    through the bracket operator. When passing a :class:`slice` object to :meth:`amdapy.amda.AMDA.get_dataset` the bracket operator is called on the :data:`data` attribute.

    .. code-block:: python

       >>> dataset[:]
                                  density  velocity_V r  ...  b radial  angle Uranus-Sun-Earth
       Time                                            ...                                  
       2010-01-01T01:00:00.000    0.005       347.811  ...    -0.002                   2.305
       2010-01-01T02:00:00.000    0.006       347.616  ...    -0.002                   2.518
       2010-01-01T03:00:00.000    0.006       347.407  ...    -0.002                   2.731
       2010-01-01T04:00:00.000    0.007       347.185  ...    -0.002                   2.938
       2010-01-01T05:00:00.000    0.008       346.966  ...    -0.002                   3.148
       2010-01-01T06:00:00.000    0.008       346.709  ...    -0.002                   3.360
       2010-01-01T07:00:00.000    0.008       346.539  ...    -0.002                   3.571

    The previous call is equivalent to :

    .. code-block:: python

       >>> dataset.data[:]

    Passing a parameter name or id to :meth:`amdapy.amda.AMDA.get_dataset` will return the corresponding
    :class:`amdapy.amda.Parameter` object. Individual parameters are retrieved by : 

    .. code-block:: python

       >>> dataset["density"]
       Parameter (id:ura_sw_n, name:density, units:cm⁻³, shape: (24,))

    """
    return self.datasetel_to_dataset(dataset_item, t_interval)
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

class CollectionItem:
  """Collection item base class. This is a base class shared by all items of the collection. All
  collection items have an id attribute.

  :param id: unique identification for the current item
  :type id: str
  """
  def __init__(self, id):
    self.id=id

class Collection:
  """This objects allows to navigate the various objects available in the AMDA database.
  """
  def __init__(self):
    """Object constructor
    """
    # get the AMDA observatory tree structure
    self.tree=get_obs_tree()
  def find(self, id):
    """Find and collection item by id. 

    :param id: id of the desired item
    :type id: str
    :return: Collection item with the right id if found, None otherwise
    :rtype: amdapy.amda.CollectionItem or None

    Iterates over all dataset objects in search for one with 
    the right id, if the id doesn't match then proceeds to check all parameters in the dataset
    before moving on to the next.

    .. code-block:: python
       
       >>> amda = amdapy.amda.AMDA()
       >>> var = amda.find("ura_sw_da")
       >>> var
       Parameter item (id:ura_sw_da, name:angle Uranus-Sun-Earth, units:deg, disp:None, dataset:tao-ura-sw, n:1)

    If we want a description of the dataset this parameter belongs to then we can do :

    .. code-block:: python

       >>> amda.collection.find(var.dataset_id)
       Dataset item (id:tao-ura-sw, name:SW / Input OMNI, start:2010-01-01 00:00:00, stop:2021-02-19 00:00:00, n_param:7)h
           Parameter item (id:ura_sw_n, name:density, units:cm⁻³, disp:None, dataset:tao-ura-sw, n:1)
           Parameter item (id:ura_sw_v, name:velocity, units:km/s, disp:None, dataset:tao-ura-sw, n:2)
           Parameter item (id:ura_sw_t, name:temperature, units:eV, disp:None, dataset:tao-ura-sw, n:1)
           Parameter item (id:ura_sw_pdyn, name:dynamic pressure, units:nPa, disp:None, dataset:tao-ura-sw, n:1)
           Parameter item (id:ura_sw_b, name:b tangential, units:nT, disp:None, dataset:tao-ura-sw, n:1)
           Parameter item (id:ura_sw_bx, name:b radial, units:nT, disp:None, dataset:tao-ura-sw, n:1)
           Parameter item (id:ura_sw_da, name:angle Uranus-Sun-Earth, units:deg, disp:None, dataset:tao-ura-sw, n:1)

    The object returned by :meth:`amdapy.amda.Collection.find` can be passed to the :meth:`amdapy.amda.AMDA.get` method to
    retrive the contents of the parameter or dataset.
    """
    # check datasets
    for d in self.iter_dataset():
      if d.id==id:
        return d
      else:
        for p in d.parameters:
          if p.id==id:
            return p
  def iter_dataset(self):
    """Collection item iterator
    
    :return: collection items
    :rtype: amdapy.amda.Collection.Item
    """
    for i in self.tree.iter_dataset():
      params=[self.Parameter(id=p.id, name=p.name, units=p.units, description=p.description, displaytype=p.displaytype, dataset_id=p.parent_dataset_id, components=self.get_component_description(p)) for p in i.parameters]
      yield self.Dataset(id=i.id, name=i.name, parameters=params, starttime=i.datastart, stoptime=i.datastop)
  def get_component_description(self, param):
    """Get collection items for the parameters components

    :param param: parameter object
    :type param: amdapy.amdaWSClient.obstree.ParameterElement
    :return: parameter component collection items
    :rtype: list of amdapy.amda.Collection.Component
    """
    return [self.Component(id=c.id, name=c.name, index=c.index) for c in param.components] 
  class Mission:
    """Object for containing mission description
    
    :param id: mission id, unique withing the AMDA context, used to retrieve complete mission description
    :type id: str
    :param name: name of the mission
    :type name: str
    :param description: optional, (default: None) description of the mission
    :type description: str
    :param startdate: mission start date
    :type startdate: datetime.datetime
    :param stopdate: mission stopdate, None if mission is not terminated
    :type stopdate: datetime.datetime
    """
    def __init__(self, id, name, descrition=None, startdate=None, stopdate=None):
      """Object constructor
      """
      self.id=id
      self.name=name
      self.description=description
      self.startdate=startdate
      self.stopdate=stopdate
  class Instrument:
    """Object for containing instrument description

    :param id: instrument identifier
    :type id: str
    :param name: name of the instrument
    :type name: str
    """
    def __init__(self, id, name):
      """Object constructor
      """
      self.id=id
      self.name=name
  class Component:
    """Parameter component description

    :param id: component id
    :type id: str
    :param name: component name
    :type name: str
    :param index: component column index
    :typa index: int
    """
    def __init__(self, id, name, index):
      """Object constructor
      """
      self.id=id
      self.name=name
      self.index=index
  class Parameter(CollectionItem):
    """Object for containing parameter descriptions

    :param id: parameter identification
    :type id: str
    :param name: name of the parameter
    :type name: str
    :param units: units
    :type units: str
    :param description: parameter description
    :type description: str
    :param displaytype: parameter display type
    :type displaytype: str
    :param dataset_id: identification of the parent dataset
    :type dataset_id: str
    :param components: list of components 
    :type components: list of amdapy.amda.Collection.Component objects
    """
    def __init__(self, id, name, units, description, displaytype, dataset_id, components=[]):
      """Object constructor
      """
      super().__init__(id)
      self.name=name
      self.units=units
      self.description=description
      self.displaytype=displaytype
      self.dataset_id=dataset_id
      self.components=components
      self.n=len(components)
      if self.n==0:
        self.n=1
    def __str__(self):
      """Parameter string representation

      :return: string representation of the current object
      :rtype: str
      """
      return "Parameter item (id:{}, name:{}, units:{}, disp:{}, dataset:{}, n:{})".format(self.id, self.name, self.units, self.displaytype, self.dataset_id, self.n)

  class Dataset(CollectionItem):
    """Object for containing dataset descriptions

    :param id: dataset identification, should be unique, used for retriving contents of the dataset
    :type id: str
    :param name: name of the dataset
    :type name: str
    :param parameters: list of parameter objects belonging to the dataset
    :type parameters: list of :class:`amdapy.amda.Collection.Parameter` objects
    :param starttime: start time
    :type starttime: datetime.datetime
    :param stoptime: stop time
    :type stoptime: datetime.datetime

    This object contains the descriptions of a dataset available in AMDA. You can acces the datasets
    unique identifier through the :data:`id` attribute that is common to all items of the collection.
    Datasets are then defined by a :data:`name`, a :data:`description` string, a list of 
    :data:`parameters` (parameter description objects of type :class:`amdapy.amda.Collection.Parameter`.

    Here is an example of a dataset description string ::

      Dataset (id:tao-ura-sw, start:2010-01-01 00:00:00, stop:2021-02-19 00:00:00, n_param:7)
         Parameter (id:ura_sw_n, name:density, units:cm⁻³, shape: (24,))
         Parameter (id:ura_sw_v, name:velocity, units:km/s, nodata)
         Parameter (id:ura_sw_t, name:temperature, units:eV, shape: (24,))
         Parameter (id:ura_sw_pdyn, name:dynamic pressure, units:nPa, shape: (24,))
         Parameter (id:ura_sw_b, name:b tangential, units:nT, shape: (24,))
         Parameter (id:ura_sw_bx, name:b radial, units:nT, shape: (24,))
         Parameter (id:ura_sw_da, name:angle Uranus-Sun-Earth, units:deg, shape: (24,))
    
    This object is intended to provide a description of the dataset containing parameter identifiers,
    name, units and other important information. Downloading the dataset is done by passing a 
    :class:`amdapy.amda.Collection.Dataset` object to the :meth:`amdapy.amda.AMDA.get_dataset` methode.

    """
    def __init__(self, id, name, parameters=[], starttime=None, stoptime=None):
      """Object constructor
      """
      super().__init__(id)
      self.name=name
      self.starttime=starttime
      self.stoptime=stoptime
      self.parameters=parameters
      self.n=len(parameters)
    def __str__(self):
      """Dataset string representation
      
      :return: Dataset string representation
      :rtype: str
      """
      a="Dataset item (id:{}, name:{}, start:{}, stop:{}, n_param:{})".format(self.id, self.name,self.starttime,self.stoptime, self.n)
      for p in self.parameters:
        a="{}\n\t{}".format(a,p)
      return a

if __name__=="__main__":
  print("Testing Collection")
  # create the AMDA connector object
  amda=AMDA()
  var=amda.collection.find("ura_sw_da")
  print(var)
  print(amda.collection.find(var.dataset_id))

  print("Getting a dataset")
  dataset_id="tao-ura-sw"
  dataset_desc = amda.collection.find(dataset_id)
  data = amda.get(dataset_desc)
  print(data)

  print("Getting dataset parameter ids")
  print([p.id for p in data.iter_parameter()])

  print("bracket operator on dataset")
  print(data["ura_sw_n"])
  print(data["ura_sw_n"].data)
  exit()

