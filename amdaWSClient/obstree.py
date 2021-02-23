"""
:file: obstree.py
:author: Alexandre Schulz
:brief: AMDA dataset tree representation.
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
  for k in el.attrib:
    if k.endswith("}id"):
      return el.attrib[k]

class ComponentElement:
  """ComponentElement class documentation. Represents a component XML element of the AMDA dataset tree
  """
  def __init__(self,el):
    self.id=get_id(el)
    self.name=el.get("name")
    self.index=el.get("Index1")
  def __str__(self):
    return "ComponentEl(id:{},name:{},index:{})".format(self.id, self.name, self.index)

class ParameterElement:
  def __init__(self, el, parent_id):
    self.id=get_id(el)
    self.name=el.get(NAME_ATTR)
    self.units=el.get(UNITS_ATTR)
    self.description=el.get(DESCRIPTION_ATTR)
    self.displaytype=el.get(DISPLAYTYPE_ATTR)
    self.parent_dataset_id=parent_id
    self.components=[ComponentElement(e) for e in el.iter(tag=COMPONENT_TAG)]
  def __str__(self):
    return "ParameterEl(id:{},name:{},units:{},disptype:{},size:{}".format(self.id,self.name, self.units,self.displaytype, len(self.components))

class DatasetElement:
  def __init__(self,el):
    self.name=el.get(NAME_ATTR)
    self.datastart=el.get(DATASTART_ATTR)
    self.datastop=el.get(DATASTOP_ATTR)
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
  def iter_dataset(self):
    for m in self.missions:
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
  
