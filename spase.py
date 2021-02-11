## SPASE management
#
#  @package amdapy
#  @file spase.py
#  @author Alexandre Schulz
#  @brief SPASE XML file management

import os
import subprocess
import argparse
import datetime
import numpy as np

from lxml import etree
from lxml.etree import tostring
from colorama import Fore, Style

## Default root path of the SPASE directory.
DEFAULT_REPOSITORY_ROOT="/home/aschulz/Documents"
## SPASE address prefix
SPASE_ADDR_PREFIX="spase://"
## Default time format
DATETIME_FORMAT="%Y-%m-%dT%H:%M:%SZ"
## Color mapping.
cmap={"g":Fore.GREEN, "r":Fore.RED, "b":Fore.BLUE}
## Color string.
#
#  Add coloring tags to text.
def strcol(s,c):
  return cmap[c]+s+Style.RESET_ALL
## SPASE XML tags
#
#  Enumeration of SPASE XML tags.
SPASE_TAG="Spase"
NUMERICALDATA_TAG="NumericalData"
INSTRUMENT_TAG="Instrument"
OBSERVATORY_TAG="Observatory"
PERSON_TAG="Person"
RESOURCEID_TAG="ResourceID"
INSTRUMENTID_TAG="InstrumentID"
REPOSITORYID_TAG="RepositoryID"
CONTACT_TAG="Contact"
PERSONID_TAG="PersonID"
ROLE_TAG="Role"
ELEMENT_TAG="Element"
STRUCTURE_TAG="Structure"
NAME_TAG="Name"
INDEX_TAG="Index"
PARAMETERKEY_TAG="ParameterKey"
COORDINATESYSTEM_TAG="CoordinateSystem"
COORDINATEREPRESENTATION_TAG="CoordinateRepresentation"
COORDINATESYSTEMNAME_TAG="CoordinateSystemName"
## SPASE types.
#
#  List of SPASE resource types.
NUMERICALDATA_TYPE="NumericalData"
INSTRUMENT_TYPE="Instrument"
OBSERVATORY_TYPE="Observatory"
PERSON_TYPE="Person"

## SpaseAddr class documentation.
#
#  SPASE resource identification representation.
class SpaseAddr(str):
  ## SpaseAddr.__init__(self,v)
  #
  #  SpaseAddr object initialization.
  #  @param self object pointer.
  #  @param v value.
  def __init__(self,v):
    super(SpaseAddr,self).__init__()
    self=v
  ## SpaseAddr.is_valid()
  #
  #  Check that the current object is a valid SPASE address.
  #  @param self object pointer.
  #  @return bool.
  def is_valid(self):
    return self.startswith(SPASE_ADDR_PREFIX)
  ## SpaseAddr.__str__(repository_root=None)
  #
  #  SpaseAddr .
  def __str__(self,repository_root=None):
    if repository_root is None:
      return self
    ## check if the associated path exists of not
    if os.path.exists(SpaseManager.resource_id_to_path(self,repository_root)):
      return strcol(self, "g")
    return strcol(self, "r")

## SpaseResource documentation.
#
#  SPASE XML file representation. Use this class to create, edit and save SPASE XML files.
class SpaseResource:
  ## SpaseResource.__init__ initialization.
  #
  #  Initialize the SpaseResource object.
  #  @param self the object pointer.
  #  @param filename absolute path to the XML file.
  def __init__(self, filename):
    ## path to XML file.
    self.filename=filename               
    ## XML content.
    parser=etree.XMLParser(remove_blank_text=True)
    self.tree=etree.parse(filename,parser)      
    ## XML namespace mapping.
    self.nsmap=self.tree.getroot().nsmap 
    if None in self.nsmap:
      self.nsmap["abc"]=self.nsmap[None]
      del self.nsmap[None]
  ## SpaseResource.is_spase_resource
  #
  #  Check if the current object contains an xml tree that is compatible 
  #  with the SPASE resource scheme.
  #  @param self object pointer.
  #  @return bool True is the root element of the tree is tagged Spase, False otherwise
  def is_spase_resource(self):
    return self.tree.getroot().tag.endswith(SPASE_TAG)
  ## SpaseResource validity check.
  #
  #  Check whether the object is a valid SpaseResource object. The object is valid if
  #  the tree attribute is a XML tree object with a root element tagged "Spase"
  #  @param self the object pointer.
  def valid(self):
    root_el=self.tree.xpath("/abc:{}".format(SPASE_TAG),namespaces=self.nsmap)
    return len(root_el)!=0
  ## SpaseResource type getter.
  #
  #  Returns the type of SPASE object the current instance represents. Return None on error.
  #  @param self the object pointer
  def resource_type(self):
    tags=[NUMERICALDATA_TAG,INSTRUMENT_TAG,OBSERVATORY_TAG,PERSON_TAG]
    for t in tags:
      ts=self.tree.xpath("/abc:{}/abc:{}".format(SPASE_TAG,t),namespaces=self.nsmap)
      if len(ts)!=0:
        return t
    return None
  ## SpaseResource id getter.
  #
  #  Returns the resource id of the SpaseResource object. Returns None on error.
  #  @param self the object pointer
  def resource_id(self):
    return self.tree.xpath("/abc:{}/*/abc:{}".format(SPASE_TAG,RESOURCEID_TAG), namespaces=self.nsmap)[0].text
  ## SpaseResource id setter.
  #
  #  Set the current resource ResourceID tag value.
  #  @param self object pointer.
  #  @param rid str new resource id value.
  def set_resource_id(self, rid):
    self.tree.xpath("/abc:{}/*/abc:{}".format(SPASE_TAG,RESOURCEID_TAG), namespaces=self.nsmap)[0].text=rid
  ## SpaseResource write.
  #
  #  Write the SpaseResource to a file.
  #  @param self the object pointer.
  #  @param filename the absolute target filename.
  def write(self, filename):
    self.tree.write(filename, xml_declaration=True, encoding="utf-8", pretty_print=True)
  ## SpaseResource Check if resource is of target type.
  #
  #  @param self object pointer
  #  @param rtype resource type (str type object)
  def is_type(self, rtype):
    p=self.tree.xpath("/abc:{}/abc:{}".format(SPASE_TAG,rtype),namespaces=self.nsmap)
    if len(p):
      return True
    return False
  ## SpaseResource : Get expected filename based on resource id.
  #
  #  Get the expected filename path for current resource id.
  #  @param self object pointer.
  #  @param repository_root (default DEFAULT_REPOSITORY_ROOT) the root of the Spase repository.
  #  @return str expected path.
  def expected_filename(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    return SpaseManager.resource_id_to_path(self.resource_id(), repository_root)
  ## SpaseResource iterate dependencies.
  #
  #  Iterate over dependencies of the current object.
  #  @param self object pointer.
  #  @return SpaseAddr object generator.
  def iter_dependency(self):
    res_id=self.resource_id()
    for e in self.tree.iter():
      if isinstance(e, etree._Element) and (not isinstance(e, etree._Comment)):
        if e.tag.endswith(REPOSITORYID_TAG):
          continue
        if not e.text is None:
          if e.text.startswith(SPASE_ADDR_PREFIX):
            if e.text!=res_id:
              addr=SpaseAddr(e.text)
              if addr.is_valid():
                yield addr
  ## SpaseResource iterate contacts.
  #
  #  Iterate over contact elements.
  #  @param self object pointe.
  #  @return Contact object generator.
  def iter_contact(self):
    for e in self.tree.iter():
      if e.tag.endswith(CONTACT_TAG):
        yield Contact(e)
  ## SpaseResource.dirty_find
  #
  #  find tag by name. Dirty way.
  #  @param self object pointer.
  #  @param tag tag we are looking for.
  #  @return etree.Element
  def dirty_find(self, tag):
    for e in self.tree.iter():
      if e.tag.endswith(tag):
        return e

## NumericalData class documentation.
#
#  Used for representing NumericalData files and their contents.
class NumericalData(SpaseResource):
  ## NumericalData initialization.
  #
  #  @param self object pointer.
  #  @param file path to the resource file.
  def __init__(self, file):
    super(NumericalData,self).__init__(file)
  ## NumericalData Iterate over parameters.
  #
  #  Yields Parameter object for each parameter defined in the numerical data file.
  #  @param self pointer to object.
  def iter_parameter(self):
    for p in self.tree.iter():
      if isinstance(p,etree._Element) and (not isinstance(p,etree._Comment)):
        if p.tag.endswith("Parameter"):
          yield Parameter(p)
  ## NumericalData Iterate over contacts.
  #
  #  Yields Contact object for each parameter defined in the numerical data file.
  #  @param self pointer to object.
  def iter_contact(self):
    for p in self.tree.iter():
      if isinstance(p,etree._Element) and (not isinstance(p,etree._Comment)):
        if p.tag.endswith("Contact"):
          yield Contact(p)
  ## NumericalData.parameter_count Count parameters.
  #
  #  Count the number of parameters contained in the current numerical data file.
  #  @param self pointer to object.
  def parameter_count(self):
    return len([p for p in self.iter_parameter()])
  ## NumericalData.contact_count Count contacts.
  #
  #  Count the number of contact objects contained in the current numerical data file.
  #  @param self pointer to object.
  def contact_count(self):
    return len([p for p in self.iter_contact()])
  ## NumericalData Check if current numerical data file contains a parameter.
  #
  #  Returns true if current file contains a parameter of name "name".
  #  @param self object pointer.
  #  @param param_id id of the desired parameter.
  def contains_parameter(self,param_id):
    for p in self.iter_parameter():
      if param_id==p.get_id():
        return True
    return False
  ## NumericalData Check current object resource id.
  #
  #  Check that the current resource id is valid.
  #  @param self object pointer.
  #  @param rid (optional) check the input id.
  #  @return bool True is the resource id is a valid SpaseAddr format. False otherwise.
  def check_resource_id(self, rid=None):
    if rid is None:
      return self.resource_id().startswith(SPASE_ADDR_PREFIX)
    return rid.startswith(SPASE_ADDR_PREFIX)
  ## NumericalData Check filename.
  #
  #  Filename must match the resource id.
  #  @param self object pointer.
  #  @param repository_root (default: DEFAULT_REPOSITORY_ROOT) root of the Spase repository.
  #  @return bool True if expected filename matches current filename, otherwise False.
  def check_filename(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    # get the expected path of the resource with current resource id.
    expected_path=self.expected_filename(repository_root)
    return expected_path==self.filename
  ## NumericalData remove parameter.
  #
  #  Remove a parameter element from the current object.
  #  @param self object pointer.
  #  @param i parameter index.
  def remove_parameter(self, i):
    if i<0:
      return
    if i>=self.parameter_count():
      return
    el=self.tree.xpath("/abc:Spase/abc:NumericalData", namespaces=self.nsmap)
    if len(el)==1:
      el[0].remove(self.get_parameter(i).root)
  ## NumericalData parameter_str()
  #
  #  get the string representation of the parameters.
  #  @param self object pointer.
  #  @param n_indent (int) = 0 number of indentation characters to insert.
  #  @param repository_root (default: DEFAULT_REPOSITORY_ROOT) root of the Spase repository.
  #  @return str parameter string representation.
  def parameter_str(self, n_indent=0, repository_root=None):
    a="{}Parameters :\n".format(n_indent*"\t")
    c=1
    for p in self.iter_parameter():
      a="{}{}{}. {}\n".format(a,"\t"*(n_indent+1),c,p.__str__())
      c=c+1
    return a
  ## NumericalData contact_str(n_indent, repository_root=None)
  #
  #  get the string representation of this objects contacts.
  #  @param self object pointer.
  #  @param n_indent number of indentation characters to insert every line.
  #  @param repository_root root of the Spase repository.
  #  @return str.
  def contact_str(self, n_indent=0, repository_root=None):
    a="{}Contact :\n".format(n_indent*"\t")
    c=1
    for p in self.iter_contact():
      a="{}{}{}. {}\n".format(a,"\t"*(n_indent+1),c,p.__str__(0,repository_root))
      c=c+1
    return a
  ## NumericalData.add_parameter
  #
  #  Add parameter to current object.
  #  @param self object pointer.
  #  @param param etree.Element object representing the parameter.
  def add_parameter(self, param):
    e=self.tree.xpath("/abc:Spase/abc:NumericalData", namespaces=self.nsmap)
    e[0].append(param)
  ## NumericalData.__str__ str representation.
  #
  #  Represent the current object as a string.
  #  @param self pointer to object
  #  @param repository_root (default: DEFAULT_REPOSITORY_ROOT) root of the Spase repository.
  #  @return str NumericalData string representation.
  def __str__(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    if self.check_resource_id():
      res_id_col=Fore.GREEN
    else:
      res_id_col=Fore.RED
    if self.check_filename(repository_root=repository_root):
      file_col=Fore.GREEN
      file_info=self.filename
    else:
      file_col=Fore.RED
      file_info="{}{}\n\t\texpected filename : {}".format(self.filename,\
                                                 Style.RESET_ALL,\
                                                 self.expected_filename())
    a="""NumericalData
    \tid               : {}
    \tfile             : {}
    \tinstrument id    : {}
    \trelease date     : {}
    \tdescription      : {}
    \tmeasurement type : {}
    \tstart date       : {}
    \tstop date        : {}
    \tcadence min      : {}
    \tcadence max      : {}
    """.format(res_id_col+self.resource_id()+Style.RESET_ALL,\
               file_col+file_info+Style.RESET_ALL,\
               self.get_instrument_id().__str__(repository_root),\
               self.get_release_date(),\
               self.get_description(),\
               self.get_measurement_type(),\
               self.get_start_date(),\
               self.get_stop_date(),\
               self.get_cadence_min(),\
               self.get_cadence_max())
    ## Parameters
    a=a+self.parameter_str(n_indent=1)
    ## Contacts
    a=a+self.contact_str(n_indent=1, repository_root=repository_root)
    ## Dependencies
    a=a+"\tDependencies :\n"
    c=1
    for d in self.iter_dependency():
      a=a+"\t\t{}. {}\n".format(c,d.__str__(repository_root))
      c=c+1
    
    ## debugging
    for d in self.iter_dependency():
      print(d)
    return a
  ## NumericalData.get_parameter get parmeter by index
  #
  #  Returns a Parameter object at index i.
  #  @param self object pointer.
  #  @param i index.
  #  @return Parameter
  def get_parameter(self, i):
    if i>=self.parameter_count():
      return None
    c=0
    for p in self.iter_parameter():
      if c==i:
        return p
      c=c+1
  ## NumericalData get contact by index
  #
  #  Returns a Contact object at index i.
  #  @param self object pointer.
  #  @param i index.
  #  @return Contact
  def get_contact(self, i):
    if i>=self.contact_count():
      return None
    c=0
    for p in self.iter_contact():
      if c==i:
        return p
      c=c+1
  ## NumericalData Get InstrumentID.
  #
  #  Get instrument id corresponding to the current numerical data file.
  #  @param self object pointer.
  #  @return str InstrumentID tag text. None on failure.
  def get_instrument_id(self):
    el=self.tree.xpath("/abc:{}/abc:{}/abc:{}".format(SPASE_TAG,NUMERICALDATA_TAG,INSTRUMENTID_TAG),namespaces=self.nsmap)
    if len(el)==0:
      return SpaseAddr("")
    if len(el)>1:
      print("More then one instrument id tag found")
    return SpaseAddr(el[0].text)
  ## NumericalData Get ObservatoryID.
  #
  #  Get observatory id corresponding to the current Numerical Data file. unused because the mission is pointed to by the instrument resource.
  #  @return None because not used for now.
  def get_mission_id(self):
    return None
  ## NumericalData.add_contact
  #
  #  Add a contact to the current object.
  #  @param self object pointer.
  #  @param contact_el contact etree.Element object.
  def add_contact(self, contact_el):
    # find the ResourceHeader element
    rh=None
    for e in self.tree.iter():
      if e.tag.endswith("ResourceHeader"):
        rh=e
    if e is None:
      return
    rh.append(contact_el)
  ## NumericalData.remove_contact
  #
  #  Remove contact from current object.
  #  @param self object pointer.
  #  @param i int.
  def remove_contact(self, i):
    if i<0:
      return
    if i>=self.contact_count():
      return
    el=None #self.tree.xpath("abc:Spase/abc:NumericalData/abc:ResourceHeader",namespaces=self.nsmap)
    for e in self.tree.iter():
      if e.tag.endswith("ResourceHeader"):
        el=e
    if not el is None:
      el.remove(self.get_contact(i).root)
  ## NumericalData.get_description
  #
  #  Get the description for the current object
  #  @param self object pointer.
  #  @return str, None if not set
  def get_description(self):
    desc_el=self.dirty_find("Description")
    return desc_el.text
  ## NumericalData.set_description
  #
  #  Set the description for current element.
  #  @param self object pointer.
  #  @param description str.
  def set_description(self, description):
    desc_el=self.dirty_find("Description")
    desc_el.text=description
  ## NumericalData.get_measurement_type
  #
  #  Get the MeasurementType value of this object.
  #  @param self object pointer.
  #  @return str.
  def get_measurement_type(self):
    return self.dirty_find("MeasurementType").text
  ## NumericalData.set_measurement_type
  #
  #  Set the MeasurementType value for this file.
  #  @param self object pointer.
  #  @param value str value.
  def set_measurement_type(self, value):
    el=self.dirty_find("MeasurementType")
    el.text=value
  ## NumericalData.get_start_date
  #
  #  Get current file StartDate tag.
  #  @param self object object.
  #  @return datetime.
  def get_start_date(self):
    sd_el=self.dirty_find("StartDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  ## NumericalData.set_start_date
  #
  #  Set the current object start date
  #  @param self object pointer.
  #  @param dt datetime object.
  def set_start_date(self, dt):
    sd_el=self.dirty_find("StartDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  ## NumericalData.get_stop_date
  #
  #  Get current file StopDate tag.
  #  @param self object object.
  #  @return datetime.
  def get_stop_date(self):
    sd_el=self.dirty_find("StopDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  ## NumericalData.set_stop_date
  #
  #  Set the current object stop date
  #  @param self object pointer.
  #  @param dt datetime object.
  def set_stop_date(self, dt):
    sd_el=self.dirty_find("StopDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  ## NumericalData.get_release_date
  #
  #  Get current file ReleaseDate tag.
  #  @param self object object.
  #  @return datetime.
  def get_release_date(self):
    sd_el=self.dirty_find("ReleaseDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  ## NumericalData.set_release_date
  #
  #  Set the current object release date
  #  @param self object pointer.
  #  @param dt datetime object.
  def set_release_date(self, dt):
    sd_el=self.dirty_find("ReleaseDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  ## NumericalData.get_cadence_min
  #
  #  Get current file CadenceMin tag.
  #  @param self object object.
  #  @return str
  def get_cadence_min(self):
    sd_el=self.dirty_find("CadenceMin")
    if sd_el is None:
      return None
    return sd_el.text
  ## NumericalData.set_cadence_min
  #
  #  Set the current object cadence min.
  #  @param self object pointer.
  #  @param cadence str.
  def set_cadence_min(self, cadence):
    sd_el=self.dirty_find("CadenceMin")
    sd_el.text=cadence
  ## NumericalData.get_cadence_max
  #
  #  Get current file CadenceMax tag.
  #  @param self object object.
  #  @return str
  def get_cadence_max(self):
    sd_el=self.dirty_find("CadenceMax")
    if sd_el is None:
      return None
    return sd_el.text
  ## NumericalData.set_cadence_max
  #
  #  Set the current object cadence min.
  #  @param self object pointer.
  #  @param cadence str.
  def set_cadence_max(self, cadence):
    sd_el=self.dirty_find("CadenceMax")
    sd_el.text=cadence
  ## NumericalData.set_component_prefix
  #
  #  Set the component name prefix for a given parameter.
  #  @param self object pointer.
  #  @param i parameter index.
  #  @param prefix prefix to apply to component names.
  def set_component_prefix(self, i, prefix):
    # get the ith Parameter object
    parameter=self.get_parameter(i)
    if not parameter is None:
      if parameter.get_size()>1:
        parameter.set_component_prefix(prefix)
  ## NumericalData.set_component_suffix
  #
  #  Set the parameter component name suffix for one of the parameters.
  #  @param self object pointer.
  #  @param param_id (int) index of the parameter we want to edit.
  #  @param suffix suffix scheme.
  def set_component_suffix(self, param_id, suffix):
    # get the ith parameter
    parameter=self.get_parameter(param_id)
    if not parameter is None:
      if parameter.get_size()>1:
        parameter.set_component_suffix(suffix)
    
## Instrument class documentation.  
#
#  Used for representing Instrument files and their contents.
class Instrument(SpaseResource):
  ## Instrument initialization.
  #
  #  @param self object pointer.
  #  @param file path to resource file.
  def __init__(self, file):
    super(Instrument,self).__init__(file)

## Observatory class documentation.
#
#  Used for representing Observatory files and their contents.
class Observatory(SpaseResource):
  ## Observatory initialization.
  #
  #  @param self object pointer.
  #  @param file path to resource file.
  def __init__(self, file):
    super(Observatory,self).__init__(file)

## Person class documentation.
#
#  Used for representing Person files and their contents.
class Person(SpaseResource):
  ## Person initialization.
  #
  #  @param self object pointer.
  #  @param file path to the resource file.
  def __init__(self, file):
    super(Person,self).__init__(file)

## XMLElement class documentation.
#
#  Class used for representing a XML element.
class XMLElement:
  ## XMLElement initialization.
  #
  #  XML element initialization.
  #  @param self object pointer.
  #  @param element root element of the current object.
  def __init__(self, element):
    ## root XML element.
    self.root=element
    ## XML namespace mapping.
    self.nsmap=element.nsmap
    if None in self.nsmap:
      self.nsmap["abc"]=self.nsmap[None]
      del self.nsmap[None]
  ## XMLElement find element.
  #
  #  Find element of current object.
  #  @param self object pointer.
  #  @param tag tag we are looking for.
  #  @return xml element object.
  def find(self, tag):
    for e in self.root.iter():
      if isinstance(e,etree._Comment):
        continue
      if e.tag.endswith(tag):
        return e
    return self.root.find("abc:{}".format(tag),namespaces=self.nsmap)

## Element class documentation.
#
#  This class represents Element tags in multidimensional timeseries Spase parameters.
class Element(XMLElement):
  ## Element.__init__ Element initialization
  #
  #  Initialize the Element object.
  #  @param self object pointer.
  #  @param el xml element
  def __init__(self, el):
    super(Element,self).__init__(el)
    ## Name of the Element
    self.name=self.get_name()
    ## Key of the Element
    self.key=self.get_key()
    ## Index of the Element
    self.index=self.get_index()
  ## Element.get_name Get element name
  #
  #  Get the current elements name.
  #  @param self object pointer.
  def get_name(self):
    return self.find(NAME_TAG).text
  ## Element.set_name
  #
  #  Set the current elements name.
  #  @param self object pointer.
  #  @param name new component name.
  def set_name(self, name):
    name_el=self.find(NAME_TAG)
    name_el.text=name
  ## Element.get_index Get element index 
  #
  #  Get the current elements index.
  #  @param self object pointer.
  def get_index(self):
    return self.find(INDEX_TAG).text
  ## Element.get_key Get element parameter key 
  #
  #  Get the current elements parameter key.
  #  @param self object pointer.
  def get_key(self):
    return self.find(PARAMETERKEY_TAG).text
  ## Element.__str__ Parameter element representation.
  #
  #  Element string representation.
  #  @param self object pointer.
  #  @param n_indent int.
  #  @return str.
  def __str__(self, n_indent=0):
    return "{}Component(key:{},name:{},i:{})".format(n_indent*"\t",self.key, self.name, self.index)

  
## Contact class documentation.
#
#  This class is used for representing Contact tags with Spase resource files.
class Contact(XMLElement):
  ## Contact class initialization.
  #
  #  @param self object pointer.
  #  @param element current element root.
  def __init__(self, element):
    super(Contact,self).__init__(element)
  ## Contact __str__(n_indent, repository_root=None)
  #
  #  Return string representation of the contact element.
  #  @param self object pointer.
  #  @param n_indent number of indentation characters to insert at every line.
  #  @param repository_root (default : None) when None then simply return str object. Otherwise check state and color accordingly.
  #  @return str
  def __str__(self, n_indent=0, repository_root=None):
    if repository_root is None:
      return "{}Contact(id:{},role:{})".format(n_indent*"\t",self.person_id(),self.role())
    person_id=self.person_id()
    if not person_id.is_valid():
      return strcol(self.__str__(n_indent=n_indent), "r")
    person_path=SpaseManager.resource_id_to_path(person_id,repository_root)
    if not os.path.exists(person_path):
      return strcol(self.__str__(n_indent=n_indent), "r")
    return strcol(self.__str__(n_indent=n_indent),"g")
  ## Contact person_id()
  #
  #  Get the person id value associated with this object. It should be a valid SpaseAddr object.
  #  @param self object pointer.
  #  @return SpaseAddr
  def person_id(self):
    return SpaseAddr(self.find(PERSONID_TAG).text)
  ## Contact role ()
  #
  #  Get the role associated with the current contact object.
  #  @param self object pointer.
  #  @return std.
  def role(self):
    return self.find(ROLE_TAG).text
  ## Contact.make_contact_xmlel (static)
  #
  #  Make a contact xml element.
  #  @param person_id SpaseAddr 
  #  @param role str.
  #  @return etree.Element.
  def make_contact_xmlel(person_id, role="GeneralContact"):
    contact_el=etree.Element("Contact")
    pid_el=etree.Element("PersonID")
    pid_el.text=person_id
    role_el=etree.Element("Role")
    role_el.text=role
    contact_el.append(pid_el)
    contact_el.append(role_el)
    return contact_el

## Parameter class documentation.
#
#  This class is used for representing Parameters within the context of the SPASE NumericalData
#  files.
class Parameter(XMLElement):
  ## Parameter.__init__ Object initialization.
  #
  #  Initialize the Parameter object. Pass the Parameter element.
  def __init__(self, parameter_element):
    super(Parameter,self).__init__(parameter_element)
  ## Parameter.get_id Get id of the Parameter object.
  #
  #  Return the id of the object as a str.
  #  @param self object pointer.
  def get_id(self):
    paramkey_el=self.find("ParameterKey")
    if not paramkey_el is None:
      return paramkey_el.text
    return None
  ## Parameter.get_name Get parameter name.
  #
  #  Return the parameter Name tag text. Returns None on failure.
  #  @param self object pointer.
  def get_name(self):
    paramname_el=self.find("Name")
    if not paramname_el is None:
      return paramname_el.text
    return None
  ## Parameter.get_ucd
  #
  #  Return the parameter Ucd tag content.
  #  @param self object pointer.
  #  @return ucd (str) None on fail.
  def get_ucd(self):
    el=self.find("Ucd")
    if el is None:
      return None
    return el.text
  ## Parameter.get_units Get parameter units.
  #
  #  Return the parameter Units tag text. Returns None on failure.
  #  @param self object pointer.
  def get_units(self):
    el=self.find("Units")
    if not el is None:
      return el.text
    return None
  ## Parameter.get_size Get size.
  #
  #  Return size of the parameter.
  #  @param self object pointer.
  def get_size(self):
    el=None
    for e in self.root.iter():
      if isinstance(e, etree._Comment):
        continue
      if e.tag.endswith("Structure"):
        el=e
    #el=self.root.find("abc:Structure", namespaces=self.nsmap)
    if el is None:
      return 1
    size_el=self.find("Size")
    if size_el is None:
      return 0
    if size_el.text is None:
      return 0
    v=0
    try:
      v=int(size_el.text)
      return v
    except:
      return 0
  ## Parameter.valid
  #
  #  Check the validity of the parameter. If size if greater then one then each component must be defined correctly.
  #  @param self object pointer.
  #  @return bool True if Parameter element is well defined.
  def valid(self):
    if self.get_size()==1:
      return True
    if self.get_size()>1:
      if self.count_elements()!=self.get_size():
        return False
      indexes=list(range(self.get_size()))
      for e in self.iter_component():
        name=e.name #e.find("abc:Name",namespaces=self.nsmap).text
        index=int( e.index) #e.find("abc:Index", namespaces=self.nsmap).text)
        key=e.key # .find("abc:ParameterKey", namespaces=self.nsmap).text
        expected_key="{}({})".format(self.get_id(), index-1)
        if key==expected_key:
          indexes.remove(index-1)
      return len(indexes)==0
    return False
  ## Parameter.iter_component
  #
  #  Iterate over component Elements
  #  @param self object pointer.
  def iter_component(self):
    if self.get_size()>1:
      struct_el=self.find(STRUCTURE_TAG)
      for e in struct_el.iter():
        if isinstance(e, etree._Comment):
          continue
        if e.tag.endswith(ELEMENT_TAG):
          yield Element(e)
  ## Parameter.component
  #
  #  Return the ith component.
  #  @param self object pointer.
  #  @param i index.
  #  @return Element.
  def component(self,i):
    if i<0 or i>=self.get_size():
      return None
    struct_el=self.find(STRUCTURE_TAG)
    c=0
    for e in struct_el.iter():
      if isinstance(e, etree._Comment):
        continue
      if e.tag.endswith(ELEMENT_TAG):
        if c==i:
          return Element(e)
        c=c+1
  ## Parameter.component_name 
  #
  #  Return name of the ith component.
  #  @param self object pointer.
  #  @param i index.
  #  @return str.
  def component_name(self,i):
    if i<0 or i>=self.get_size():
      return None
    el=self.component(i)
    return el.name
  ## Parameter.__str__ object string representation.
  #
  #  Return string representation of the current object.
  #  @param self object pointer.
  #  @param n_indent number of indentation characters to insert at begining of each line.
  #  @return str
  def __str__(self,n_indent=0):
    if self.get_size()==1:
      s="{}Parameter(key:{},name:{},size:{},disp_type:{})".format(n_indent*"\t",\
                                                                self.get_id(),\
                                                                self.get_name(),\
                                                                self.get_size(),\
                                                                self.get_display_type())
    else:
        s="{}Parameter(key:{},name:{},size:{},disp_type:{},cprefix:{},cscheme:{})".format(n_indent*"\t",\
                                                                self.get_id(),\
                                                                self.get_name(),\
                                                                self.get_size(),\
                                                                self.get_display_type(),\
                                                                self.get_component_prefix(),\
                                                                self.get_component_suffix())

    if self.get_size()>1:
      s=s+"\n"
      for i in range(self.get_size()):
        s=s+"{}{}. {}\n".format((n_indent+1)*"\t", i+1, self.component(i))
    if self.valid():
      return strcol(s,"g")
    return strcol(s,"r")
  ## Parameter.get_component_prefix
  #
  #  Get the component prefix for the current parameter.
  #  @param self object pointer.
  def get_component_prefix(self):
    #print("in Parameter.get_component_prefix : self.size={}".format(self.get_size()))
    #print("self.component_count/count_element : {}".format(self.count_elements()))
    if self.get_size()==1:
      return None
    if self.count_elements()==0:
      return None
    # iterate over components.
    component_names=[c.name for c in self.iter_component()]
    return self.get_similar_prefix(np.array(component_names,dtype=object))
  ## Parameter.set_component_prefix
  #
  #  Set the current objects component prefix.
  #  @param self object pointer.
  #  @param prefix str.
  def set_component_prefix(self, prefix):
    if self.get_size()!=1:
      # get the current prefix value
      old_prefix=self.get_component_prefix()
      if len(old_prefix):
        for component in self.iter_component():
          # get component name
          cname=component.name
          newcname="{}{}".format(prefix,cname[len(old_prefix):])
          component.set_name(newcname)
  ## Parameter.get_component_suffix
  #
  #  Get the components suffix scheme. For example the scheme could be xyz.
  #  @param self object pointer.
  #  @return str suffix scheme, empty string on failure.
  def get_component_suffix(self):
    if self.get_size()==1:
      return ""
    # first try to determine the parameter components prefix
    prefix=self.get_component_prefix()
    if prefix is None:
      return ""
    if len(prefix):
      a=""
      for c in self.iter_component():
        a="{}{}".format(a,c.name.replace(prefix,""))
      return a
    else:
      # no component prefix could be found.
      return ""
  ## Parameter.set_component_suffix
  #
  #  Set the component suffix scheme.
  #  @param self object pointer.
  #  @param scheme (str) 
  def set_component_suffix(self,scheme):
    # first get the prefix
    prefix=self.get_component_prefix()
    # if the new scheme length is smaller then the number of components then do nothing
    if len(scheme) < self.get_size():
      print("Scheme is to short. leaving.")
      input()
      return
    i=0
    for c in self.iter_component():
      c.set_name("{}{}".format(prefix,scheme[i]))
      i=i+1
  ## Parameter.get_similar_prefix
  #
  #  Iterate over component names and search for a common prefix.
  #  @param self object pointer.
  #  @param name_list list of component names
  #  @param n (default: None) int.
  def get_similar_prefix(self,name_list, n=None):
    #print("in Parameter.get_similar_prefix : name_list={}, n={}".format(name_list, n))
    #print("self.size : {}".format(self.get_size()))
    if isinstance(name_list,list):
      name_list=np.array(name_list,dtype=object)
    if n==0:
      return ""
    if n is None:
      size_list=np.array([len(name) for name in name_list])
      if np.all(size_list == size_list[0]):
        # all names are the same size
        return self.get_similar_prefix(name_list,n=size_list[0])
      else:
        min_size=np.min(size_list)
        return self.get_similar_prefix([name[:min_size] for name in name_list], min_size)
    else:
      n_l=np.array([name[:n] for name in name_list],dtype=object)
      if np.all(n_l == n_l[0]):
        return n_l[0]
      else:
        return self.get_similar_prefix([name[:n-1] for name in name_list], n-1)
  ## Parameter.count_elements Count Elements
  # 
  #  Count Element tags.
  #  @param self object pointer.
  #  @return int number of Element tags.
  def count_elements(self):
    c=0
    for e in self.root.iter():
      if isinstance(e, etree._Comment):
        continue
      if e.tag.endswith("Element"):
        c=c+1
    return c
  ## Parameter.numericaldata_empty_str() Parameter string representation.
  #
  #  String representation of the Parameter object. For debugging purposes.
  #  @param self object pointer.
  def numericaldata_empty__str__(self):
    if self.valid():
      return Fore.GREEN+"Parameter (id:{}, name:{}, units:{}, size:{})".format(self.get_id(), self.get_name(),self.get_units(), self.get_size())+Style.RESET_ALL
    return Fore.RED+"Parameter (id:{}, name:{}, units:{}, size:{})".format(self.get_id(), self.get_name(),self.get_units(), self.get_size())+Style.RESET_ALL
  ## Parameter.make_parameter_element
  #
  #  Make a new Parameter object.
  #  @param name name of the parameter.
  #  @param key key of the parameter.
  #  @param size int size.
  #  @param component_prefix (default "u") prefix of all component names.
  #  @param rhint (default "TimeSeries") resource type.
  #  @return Parameter object.
  @staticmethod
  def make_parameter_xmlel(name, key, size=1, component_prefix="u", rhint="TimeSeries"):
    print("making parameter : name: {}, key: {}, size:{}, component_prefix:{}".format(name,\
                                                                                      key,\
                                                                                      size,\
                                                                                      component_prefix,\
                                                                                      rhint))
    p_el=etree.Element("Parameter")
    name_el=etree.Element("Name")
    name_el.text=name
    param_key_el=etree.Element("ParameterKey")
    param_key_el.text=key
    ucd_el=etree.Element("Ucd")
    units_el=etree.Element("Units")
    rendh_el=etree.Element("RenderingHints")
    disp_el=etree.Element("DisplayType")
    disp_el.text=rhint
    rendh_el.append(disp_el)
    p_el.append(name_el)
    p_el.append(param_key_el)
    p_el.append(ucd_el)
    p_el.append(units_el)
    p_el.append(rendh_el)
    if size>1:
      struct_el=Parameter.make_structure_xmlel(size, name_prefix="u", parameter_key=key)
      p_el.append(struct_el)
    return p_el
  ## Parameter.make_structure_xmlel
  #
  #  Make the Structure xml element for multidimensional parameters.
  #  @param size int.
  #  @param name_prefix (default : "u") component name prefix.
  #  @param parameter_key parameter key
  #  @return etree.Element
  @staticmethod
  def make_structure_xmlel(size, name_prefix="u", parameter_key=""):
    s=etree.Element("Structure")
    size_el=etree.Element("Size")
    size_el.text=str(size)
    s.append(size_el)
    for i in range(size):
      el=etree.Element("Element")
      name_el=etree.Element("Name")
      name_el.text=name_prefix+"xyzabc"[i]
      index_el=etree.Element("Index")
      index_el.text=str(i+1)
      pk_el=etree.Element("ParameterKey")
      pk_el.text="{}({})".format(parameter_key,i)
      el.append(name_el)
      el.append(index_el)
      el.append(pk_el)

      s.append(el)
    return s
  ## Parameter.get_display_type
  #
  #  Get the current parameter display type.
  #  @param self object pointer.
  #  @return str
  def get_display_type(self):
    e=self.find("DisplayType")
    if e is None:
      return None
    return e.text
  ## Parameter.set_display_type
  #
  #  Set the current object display type.
  #  @param self object pointer.
  #  @param value value of DisplayType tag.
  def set_display_type(self,value):
    e=self.find("DisplayType")
    if not e is None:
      e.text=value
  ## Parameter.has_coordinate_system
  #
  #  Check if the current object has a coordinate system tag
  #  @param self object pointer.
  #  @return bool True is object contains a coordinate system tag, False otherwise.
  def has_coordinate_system(self):
    el=self.find(COORDINATESYSTEM_TAG)
    if el is None:
      return False
    return True
  ## Parameter.get_coordinate_system_name
  #
  #  Get the current parameter coordinate system name.
  #  @param self object pointer.
  #  @return str coordinate system name. None on failure.
  def get_coordinate_system_name(self):
    el=self.find(COORDINATESYSTEMNAME_TAG)
    if el is None:
      return None
    return el.text
## SpaseManager class.
#
#  Used for managing SpaseResource objects.
class SpaseManager:
  ## SpaseManager initialization
  #
  #  @param self the object pointer
  #  @param root the root path. Search for xml files stored under root directory.
  def __init__(self, root):
    ## Root of the repository.
    self.root=root
  ## SpaseManager.iter_xml_file_path Iterate over XML file paths
  # 
  #  @param self the object pointer.
  #  @param path path at which to start iterating
  def iter_xml_file_path(self,path=None):
    if path is None:
      for p in self.iter_xml_file_path(path=self.root):
        yield p
    else:
      for root,dirs,files in os.walk(path):
        for f in files:
          if f.endswith(".xml"):
            yield os.path.join(root,f)
  ## SpaseManager.iter_resource Iterate over SpaseResource objects.
  #
  #  Yields every SpaseResource object found.
  #  @param self pointer to the object.
  #  @param rtype resource type.
  def iter_resource(self, rtype=None):
    for p in self.iter_xml_file_path():
      res=None
      try:
        res=SpaseResource(p)
      except:
        continue
      # check that the resource is a Spase object (unless we want to keep all xml files encountered
      if not res.is_spase_resource():
        continue
      if rtype is None:
        yield res
      else:
        if res.is_type(rtype):
          yield res
  ## SpaseManager.iter_numerical_data Iterate over NumericalData files.
  #
  #  Yield a NumericalData object for each resource found that is of right type.
  #  @param self object pointer.
  def iter_numerical_data(self):
    for r in self.iter_resource(rtype=NUMERICALDATA_TYPE):
      yield NumericalData(r.filename)
  ## SpaseManager.iter_instrument Iterate over Instrument files.
  #
  #  Yield a Instrument object for each resource found that is of right type.
  #  @param self object pointer.
  def iter_instrument(self):
    for r in self.iter_resource(rtype=INSTRUMENT_TYPE):
      yield Instrument(r.filename)
  ## SpaseManager.iter_observatory Iterate over Observatory files.
  #
  #  Yield a Observatory object for each resource found that is of right type.
  #  @param self object pointer.
  def iter_observatory(self):
    for r in self.iter_resource(rtype=OBSERVATORY_TYPE):
      yield Observatory(r.filename)
  ## SpaseManager.iter_person Iterate over Person files.
  #
  #  Yield a Person object for each resource found that is of right type.
  #  @param self object pointer.
  def iter_person(self):
    for r in self.iter_resource(rtype=PERSON_TYPE):
      yield Person(r.filename)
  ## SpaseManager.health_check Health check. 
  #
  #  Check repository health status. Look for corrupted resources, duplicates, resources
  #  with wrong id, etc
  #  @param self object pointer.
  def health_check(self):
    duplicated_ids=self.get_duplicate_ids()
    if len(duplicated_ids):
      print("Duplicates found : {}".format(len(duplicated_ids)))
      #print(duplicated_ids)
      for d in duplicated_ids:
        print("Duplicate : {}".format(d))
        for dup in duplicated_ids[d]:
          path_corresponds_to_id=dup==self.resource_id_to_path(d,repository_root=self.root)
          if path_corresponds_to_id:
            print("\t\t{} orig".format(dup))
          else:
            # get the correct id for current file
            correct_id=self.path_to_resource_id(dup)
            print("\t\t{}".format(dup))
            print("\t\t\t{}".format(correct_id))
            # check if there are resources with the same id
            res_l=self.get_resource_by_id(correct_id)
            print("\t\t\tResources with correct id : {}".format(len(res_l)))
            # check if the file corresponding to that id already exists
            if os.path.exists(self.resource_id_to_path(correct_id, repository_root=self.root)):
              cmd="diff {} {}".format(self.resource_id_to_path(correct_id,repository_root=self.root), dup)
              print(cmd)
              r=subprocess.check_output(cmd.split(" "))
              print(r)
        print("")
  ## SpaseManager.get_duplicate_ids Check for duplicate resources.
  #
  #  Resources are uniquely identified by their ResourceID value. If the repository contains
  #  multiple SPASE resource files with the same ResourceID value it may cause errors. 
  #  Returns a dictionary indexed by the duplicated ResourceID values and with values the list
  #  of files containing the corresponding id.
  #  @param self object pointer.
  #  @return dict(ResourceID, list(str)) dictionary indexed by ResourceID encountered more then once, and with value a list of files having the corresponding id.
  def get_duplicate_ids(self):
    id_list={}
    duplicates={}
    for res in self.iter_resource():
      res_id=res.resource_id()
      if not res_id in id_list:
        id_list[res_id]=res.filename
      else:
        # the resource id has already been encountered
        if not res_id in duplicates:
          duplicates[res_id]=[id_list[res_id], res.filename]
        else:
          duplicates[res_id].append(res.filename)
    return duplicates
  ## SpaseManager.get_resource_by_id Get a SpaseResource object by ID.
  #
  #  Return object matching given ResourceID.
  #  @param self object pointer.
  #  @param res_id std resource id of desired SPASE object.
  #  @return list (SpaseResource) of objects with input id. In a healthy repository we only expect the list to be of length one.
  def get_resource_by_id(self, res_id):
    a=[]
    for res in self.iter_resource():
      if res.resource_id()==res_id:
        a.append(res)
    return a
  ## SpaseManager.resource_id_to_path (static) Get absolute path from resource id.
  #
  #  Returns absolute expected path of a SpaseResource with a desired ResourceID.
  #  @param res_id resource id.
  #  @param repository_root root of the repository.
  #  @return str absolute path corresponding to input resource id.
  @staticmethod
  def resource_id_to_path(res_id, repository_root):
    t=res_id.replace(SPASE_ADDR_PREFIX, "")
    return os.path.join(repository_root, "{}.xml".format(t))
  ## SpaseManager.path_to_resource_id (static) Get resource id from path.
  #
  #  Returns resource id corresponding to a file stored at the desired path.
  #  @param path str resource path.
  #  @param repository_root root of the repository.
  #  @return str resource id corresponding to the input path.
  @staticmethod
  def path_to_resource_id(path, repository_root):
    t=path.replace(repository_root, "")
    if t.startswith("/"):
      t=t[1:]
    return "{}{}".format(SPASE_ADDR_PREFIX, t.replace(".xml",""))
  ## SpaseManager.get_bad_ids Check for resources whose ResourceID value does not correspond to their path.
  #
  #  Get bad ided resources.
  #  @param self object pointer.
  #  @return list of (filename, id) tuples
  def get_bad_ids(self):
    a=[]
    for r in self.iter_resource():
      path=r.filename
      id_=r.resource_id()
      id_path=self.resource_id_to_path(id_)
      if path!=id_path:
        a.append((path, id_))
    return a
  ## SpaseManager.find_resource Find resource file.
  #
  #  Find a SPASE resource file by name.
  #  @param name expected filename.
  #  @return SpaseResource object, None on failure.
  def find_resource(self,name):
    cmd="find {}/ -type f -name '*{}.xml'".format(self.root, name)
    os.system(cmd)
    path=list(filter(None,get_cmd_output(cmd).split("\n")))
    if len(path)==1:
      print("ONE RESOURCE FOUND")
      return SpaseResource(path[0])
    elif len(path)>1:
      print("MORE THEN ONE RESOURCE FOUND WITH THE NAME {}".format(name))
      return SpaseResource(path[0])
    else:
      print("RESOURCE DOES NOT EXIST")
      return None

## Run system command 
#
#  Run system command and return output as string.
#  @param cmd system command we want to run.
#  @return str command output
def get_cmd_output(cmd):
  os.system("{} > temp.output".format(cmd))
  a=""
  with open("temp.output","r") as f:
    a=f.read()
    f.close()
  os.system("rm temp.output")
  return a

     
## Parse arguments.
#
#  Parse command line arguments.
def parse_args():
  parser=argparse.ArgumentParser()
  parser.add_argument("--duplicates",help="show duplicate resources.", action="store_true")
  parser.add_argument("-l","--list", help="list resources.", action="store_true")
  parser.add_argument("-p","--person", help="focus Person resources.", action="store_true")
  parser.add_argument("-o","--observatory", help="focus Observatory resources.", action="store_true")
  parser.add_argument("-i","--instrument", help="focus Instrument resources.", action="store_true")
  parser.add_argument("-n","--numericaldata", help="focus NumericalData resources", action="store_true")
  parser.add_argument("-r","--root", help="set root directory.", type=str, default=DEFAULT_REPOSITORY_ROOT)
  parser.add_argument("--listbad", help="list bad files.", action="store_true")
  parser.add_argument("-e","--edit", help="start resource editor.", action="store_true")
  parser.add_argument("-f","--find",help="find resource file by name.",type=str, default="")
  return parser.parse_args()

## Resource list from arguments.
#
#  Get list of focused resource types from the command line arguments.
def rtype_from_args(args):
  rtype=[]
  if args.person:
    rtype.append(PERSON_TYPE)
  if args.observatory:
    rtype.append(OBSERVATORY_TYPE)
  if args.instrument:
    rtype.append(INSTRUMENT_TYPE)
  if args.numericaldata:
    rtype.append(NUMERICALDATA_TYPE)
  if len(rtype)==0:
    return None
  return rtype

## ---------------------------------------MAIN-----------------------------------
#
#  Main function.
if __name__=="__main__":
  args=parse_args()

  # initialize the SPASE resource manager.
  repo_path=args.root
  print("Initializing the SpaseManager at {}".format(repo_path))
  man=SpaseManager(repo_path)

  if args.list:
    rtype=rtype_from_args(args)
    if rtype is None:
      for r in man.iter_resource():
        res_type=r.resource_type()
        res_id=r.resource_id()
        res_valid=r.valid()
        print("{} : {} valid:{}".format(res_type, res_id, res_valid))
    else:
      for t in rtype:
        for r in man.iter_resource(rtype=t):
          res_type=r.resource_type()
          res_id=r.resource_id()
          res_valid=r.valid()
          print("{} : {} valid:{}".format(res_type, res_id, res_valid))
  if args.listbad:
    badids=man.get_bad_ids()
    for filename,id_ in badids:
      print("BADID : {} : {}".format(filename,id_))
    print("Number of bad id'd files : {}".format(len(man.get_bad_ids())))
  if len(args.find):
    print("Searching for resource by name : {}".format(args.find))
    print(man.find_resource(args.find))

  if args.edit:
    create_numerical_data("numericaldata_empty.xml")
