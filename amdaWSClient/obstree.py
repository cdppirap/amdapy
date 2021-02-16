"""
:file: obstree.py
:author: Alexandre Schulz
:brief: AMDA dataset tree representation.
"""

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
  def __init__(self, el):
    self.id=get_id(el)
    self.name=el.get(NAME_ATTR)
    self.units=el.get(UNITS_ATTR)
    self.description=el.get(DESCRIPTION_ATTR)
    self.displaytype=el.get(DISPLAYTYPE_ATTR)
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
    self.parameters=[ParameterElement(e) for e in el.iter(tag=PARAMETER_TAG)]
  def __str__(self):
    return "DatasetEl(id:{},name:{},start:{},stop:{},n_param:{})".format(self.id,self.name,self.datstart, self.datastop,len(self.parameters))
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

class ObsTree:
  def __init__(self, tree):
    self.missions=[MissionElement(e) for e in tree.iter(tag=MISSION_TAG)]
  def iter_dataset(self):
    for m in self.missions:
      for d in m.iter_dataset():
        yield d
  
