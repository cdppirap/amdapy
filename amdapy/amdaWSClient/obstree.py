"""
:file: obstree.py
:author: Alexandre Schulz
:brief: AMDA dataset tree representation.

Using the :meth:`amdapy.amdaWSClient.client.get_obs_tree` method we can retrieve an XML file containing
descriptions of all available datasets, and the parameters therein. The :class:`ObsTree` is used for 
parsing the elements of the XML file and returning dataset and parameter descriptions. Since the 
:mod:`amdapy.amdaWSClient.client` module provides functions for retrieving *datasets* and *parameters*, 
navigating the AMDA catalogue involves gathering descriptions of datasets and parameters. It is noted
that in AMDA all datasets are timeseries. Although nothing specific to timeseries has yet been implemented
it is good to keep this in mind.

Datasets are described by :
    - id, which is unique within AMDA
    - name, as presented in the navigation tree on the AMDA web plateform
    - mission name
    - instrument name
    - start datetime
    - stop datetime
    - list of parameters

Parameter descriptions include :
    - id, parameter ids are unique within AMDA
    - name, as presented in the navigation tree on the AMDA web plateform
    - display type, string indicating if the data should be presented as a plot or a spectrogram
    - description, a description of the parameter
    - units, units in which the parameter is expressed
    - parent id, dataset id
    - list of components if any. If no components then parameter is considered a scalar

"""
import datetime


"""Tags
"""
DATACENTER_TAG="dataCenter"
MISSION_TAG="mission"
INSTRUMENT_TAG="instrument"
DATASET_TAG="dataset"
PARAMETER_TAG="parameter"
COMPONENT_TAG="component"

"""Attributes
"""
NAME_ATTR="name"
UNITS_ATTR="units"
DESCRIPTION_ATTR="description"
DISPLAYTYPE_ATTR="display_type"
DATASTART_ATTR="dataStart"
DATASTOP_ATTR="dataStop"
LASTUPDATE_ATTR="lastUpdate"
DESC_ATTR="desc"
DATASOURCE_ATTR="dataSource"
SPASEID_ATTR="spaseId"
SAMPLING_ATTR="sampling"
TARGET_ATTR="target"
ATT_ATTR="att"

"""Constants
"""
MISSIONDEPENDENT_DATE="MissionDependent"
DATE_FORMAT="%Y-%m-%dT%H:%M:%SZ"

def get_id(el):
  """Get id of an element. Searches for an attribut {<namespace>}id and returns value

  :return: id of the element, None if no :data:`id` attribute was found
  :rtype: str or NoneType
  """
  for k in el.attrib:
    if k.endswith("}id"):
      return el.attrib[k]

class ComponentElement:
  """Simple container class. Contains description of the parameters components. Store the id, name,
  and index of the component.

  :param el: XML element
  :type el: lxml.etree._Element
  """
  def __init__(self,el):
    """Object constructor
    """
    self.id=get_id(el)
    self.name=el.get("name")
    self.index=el.get("Index1")
  def __str__(self):
    """Get a string representation of the current component object. 

    :return: string representation of the component
    :rtype: str
    """
    return "Component(id:{},name:{},index:{})".format(self.id, self.name, self.index)

class ParameterElement:
  """Container for storing parameter descriptions. This object is initialized by passing an XML element
  whith the "parameter" tag and an id of the parent dataset. It allows acces to the parameters id,
  name, units, description, displaytype, parent_dataset_id and a list of components
"""
  def __init__(self, el, parent_id):
    self.id=get_id(el)
    self.name=el.get(NAME_ATTR)
    self.units=el.get(UNITS_ATTR)
    self.description=el.get(DESCRIPTION_ATTR)
    self.displaytype=el.get(DISPLAYTYPE_ATTR)
    self.parent_dataset_id=parent_id
    self.components=[ComponentElement(e) for e in el.iter(tag=COMPONENT_TAG)]
  def __str__(self):
    """ParameterElement string representation

    :return: current object string representation
    :rtype: str
    """
    return "ParameterEl(id:{},name:{},units:{},disptype:{},size:{})".format(self.id,self.name, self.units,self.displaytype, len(self.components))
  def component_count(self):
    """Count components

    :return: number of components of the current parameter
    :rtype: int
    """
    return len(self.components)
  def size(self):
    """Get number of components

    :return: number of components
    :rtype: int
    """
    return len(self.components)
  def iter_component(self):
    """Component iterator

    :return: components one by one
    :rtype: amdapy.amdaWSClient.obstree.ComponentElement
    """
    for c in self.components:
      yield c
class DatasetElement:
  def __init__(self,el):
    self.name=el.get(NAME_ATTR)
    self.datastart=el.get(DATASTART_ATTR)
    self.datastop=el.get(DATASTOP_ATTR)
    try:
      self.datastart=datetime.datetime.strptime(self.datastart, DATE_FORMAT)
    except:
      self.datastart=None
    try:
      self.datastop=datetime.datetime.strptime(self.datastop,DATE_FORMAT)
    except:
      self.datastop=None
    self.lastupdate=el.get(LASTUPDATE_ATTR)
    self.description=el.get(DESC_ATTR)
    self.datasource=el.get(DATASOURCE_ATTR)
    self.id=get_id(el)
    self.spaseid=el.get(SPASEID_ATTR)
    self.sampling=el.get(SAMPLING_ATTR)
    self.target=el.get(TARGET_ATTR)
    self.att=el.get(ATT_ATTR)
    self.parameters=[ParameterElement(e,parent_id=self.id) for e in el.iter(tag=PARAMETER_TAG)]
  def __str__(self):
    return "DatasetEl(id:{},name:{},start:{},stop:{},n_param:{})".format(self.id,self.name,self.datastart, self.datastop,len(self.parameters))
  def iter_parameter(self, units=None):
      for p in self.parameters:
          if units is None:
              yield p
          else:
              if units==p.units:
                  yield p
  def timespan(self):
    # start time
    start=None
    stop=None
    if not (self.datastart==MISSIONDEPENDENT_DATE or len(self.datastart)==0):
      start=datetime.datetime.strptime(self.datastart, DATE_FORMAT)
    if not (self.datastop==MISSIONDEPENDENT_DATE or len(self.datastop)==0):
      stop=datetime.datetime.strptime(self.datastop, DATE_FORMAT)
    return start,stop
class InstrumentElement:
  def __init__(self, el):
    self.name=el.get(NAME_ATTR)
    self.description=el.get(DESC_ATTR)
    self.id=get_id(el)
    self.att=el.get(ATT_ATTR)
    self.datasets=[DatasetElement(e) for e in el.iter(tag=DATASET_TAG)]
  def __str__(self):
    return "InstrumentEl(id:{},name:{},n_dataset:{})".format(self.id, self.name, len(self.datasets))
  def iter_dataset(self):
    for d in self.datasets:
      yield d
  def iter_parameter(self, units=None):
      for d in self.datasets:
          for p in d.iter_parameter(units=units):
              yield p
class MissionElement:
  def __init__(self, el):
    self.id=get_id(el)
    self.name=el.get(NAME_ATTR)
    self.description=el.get(DESC_ATTR)
    self.target=el.get(TARGET_ATTR)
    self.att=el.get(ATT_ATTR)
    self.instruments=[InstrumentElement(e) for e in el.iter(INSTRUMENT_TAG)]
  def find_instrument(self, instrument_name):
    """Find instrument by name

    :param instrument_name: instrument name
    :type instrument_name: str
    :return: instrument if found , None otherwise
    :rtype: amdapy.amdaWSClient.obstree.InstrumentElement or None
    """
    for i in self.instruments:
        if i.name == instrument_name:
            return i
    return None
  def __str__(self):
    return "MissionEl(id:{},name:{},n_instrument:{})".format(self.id,self.name,len(self.instruments))
  def iter_dataset(self):
    for i in self.instruments:
      for d in i.iter_dataset():
        yield d
  def iter_parameter(self, units=None):
      for instrument in self.instruments:
          for p in instrument.iter_parameter(units=units):
              yield p

class ObsTree:
  MISSION=1
  DATASET=2
  PARAMETER=3
  COMPONENT=4
  def __init__(self, tree):
    self.missions=[MissionElement(e) for e in tree.iter(tag=MISSION_TAG)]
  def iter_dataset(self, mission=None, instrument=None):
    if not mission is None:
      # find the mission
      m=self.find_mission(mission)
      if m is None:
        # mission does not exist
        return
      if not instrument is None:
        # get the instrument
        i=m.find_instrument(instrument)
        if i is None:
          # instrument was not found return None
          return
        # yield datasets belonging to the instrument
        for dataset in i.iter_dataset():
          yield dataset
    else:
      # iterate over all missions
      for m in self.missions:
        if not instrument is None:
          # find instrument
          i=m.find_instrument(instrument)
          if not i is None:
            for d in i.iter_dataset():
              yield dataset
        else:
          # yield all datasets
          for d in m.iter_dataset():
            yield d
  def iter_mission(self,target=None):
      for m in self.missions:
          if not target is None:
              if m.target==target:
                  yield m
          else:
              yield m
  def iter_parameter(self, units=None):
      for m in self.missions:
          for p in m.iter_parameter(units=units):
              yield p
  def find_parameter(self,param_id):
      for p in self.iter_parameter():
          if p.id==param_id:
              return p
  def find_mission(self,name):
      for m in self.iter_mission():
          if m.name==name:
              return m
  def find_dataset(self, dataset_id):
      for d in self.iter_dataset():
          if d.id==dataset_id:
              return d
  def parameter_timespan(self, parameter_id):
      param_obj=self.find_parameter(parameter_id)
      if param_obj is None:
          return None
      # get the parent dataset
      dataset_obj=self.find_dataset(param_obj.parent_dataset_id)
      return dataset_obj.datastart,dataset_obj.datastop
  
