"""Container for containing the collection of parameters on AMDA
"""
from amdapy.rest.client import get_obs_tree

class _CollectionItem:
  """Collection item base class. This is a base class shared by all items of the collection. All
  collection items have an id attribute.

  :param id: unique identification for the current item
  :type id: str
  """
  def __init__(self, id):
    self.id=id

class Collection:
  """The :class:`Collection` object is used for getting descriptions of the items in AMDAs database.
  Navigation the database is done with the :meth:`Collection.iter_dataset` iterator.
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
    :rtype: amdapy.amda._CollectionItem or None

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
      params=[self.Parameter(id=p.id, name=p.name, units=p.units, description=p.description, displaytype=p.displaytype, dataset_id=p.parent_dataset_id, components=self._get_component_description(p)) for p in i.parameters]
      yield self.Dataset(id=i.id, name=i.name, parameters=params, globalstart=i.datastart, globalstop=i.datastop)
  def _get_component_description(self, param):
    """Get collection items for the parameters components

    :param param: parameter object
    :type param: amdapy.rest.obstree.ParameterElement
    :return: parameter component collection items
    :rtype: list of amdapy.amda.Collection._Component
    """
    return [self._Component(id=c.id, name=c.name, index=c.index) for c in param.components] 
  class _Mission:
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
  class _Instrument:
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
  class _Component:
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
  class Parameter(_CollectionItem):
    """This object contains parameter descriptions.

    .. warning::

      Parameter descriptions do not contain any information about the data timespan, to get the
      begining and end date of the data you must retrieve the parent dataset whose id is given by the
      :data:`dataset_id` attribute.

    You can access the following information through this container : 
       * id : unique parameter id
       * name : parameter name
       * units : data units
       * dataset_id : parent dataset id
       * components : list of components, only if these are available in AMDA

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
    :type components: list of amdapy.amda.Collection._Component objects
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

  class Dataset(_CollectionItem):
    """This object contains a description of a dataset. Attributes are:
       * id : unique identifier for the dataset
       * name : name of the dataset in AMDAs navigation tree
       * globalstart: data start time (:class:`datetime.datetime` )
       * globalstop: data stop time (:class:`datetime.datetime`)
       * parameters : list of parameter descriptions (:class:`amdapy.amda.Collection.Parameter`)
       * n : number of parameters

    :param id: dataset identification, should be unique, used for retriving contents of the dataset
    :type id: str
    :param name: name of the dataset
    :type name: str
    :param parameters: list of parameter objects belonging to the dataset
    :type parameters: list of :class:`amdapy.amda.Collection.Parameter` objects
    :param globalstart: start time
    :type globalstart: datetime.datetime
    :param globalstop: stop time
    :type globalstop: datetime.datetime

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
    def __init__(self, id, name, parameters=[], globalstart=None, globalstop=None):
      """Object constructor
      """
      super().__init__(id)
      self.name=name
      self.globalstart=globalstart
      self.globalstop=globalstop
      self.parameters=parameters
      self.n=len(parameters)
    def __str__(self):
      """Dataset string representation
      
      :return: Dataset string representation
      :rtype: str
      """
      a="Dataset item (id:{}, name:{}, global_start:{}, global_stop:{}, n_param:{})".format(self.id, self.name,self.globalstart,self.globalstop, self.n)
      for p in self.parameters:
        a="{}\n\t{}".format(a,p)
      return a

