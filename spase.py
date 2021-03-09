"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: spase.py
:brief: Classes and functions for manipulating SPASE XML resource files
"""

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

def strcol(s,c):
  """Format a string to print in color

  :param s: string to print
  :type s: str
  :param c: color
  :type c: colorama.Style.Color
  :return: colored string
  :rtype: str
  """
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
  """SPASE resource address container. Contains the address of a SPASE resource with respect to its root
  directory.

  :param v: value
  :type v: str
  """
  def __init__(self,v):
    super(SpaseAddr,self).__init__()
    self=v
  def is_valid(self):
    """Check if the current object is a valid address
    :return: True is the current object is a valid SPASE address, False otherwise
    :rtype: bool
    """
    return self.startswith(SPASE_ADDR_PREFIX)
  def __str__(self,repository_root=None):
    """String representation of the current object
    
    :param repository_root: path to the root of the SPASE repository, optional
    :type repository_root: str
    :return: string representation of the current object
    :rtype: str
    """
    if repository_root is None:
      return self
    ## check if the associated path exists of not
    if os.path.exists(SpaseManager.resource_id_to_path(self,repository_root)):
      return strcol(self, "g")
    return strcol(self, "r")

class SpaseResource:
  """Base class for representing SPASE resources

  :param filename: path to the resource file
  :type filename: str
  """
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
  def is_spase_resource(self):
    """Check that the current object is compatible with the SPASE XML scheme

    :return: True if current object is a valid spase resource, False otherwise
    :rtype: bool
    """
    return self.tree.getroot().tag.endswith(SPASE_TAG)
  def valid(self):
    """Check that the current object is valid

    :return: True if the current object is a valid SPASE resource object
    :rtype: bool
    """
    root_el=self.tree.xpath("/abc:{}".format(SPASE_TAG),namespaces=self.nsmap)
    return len(root_el)!=0
  def resource_type(self):
    """Get resource type

    :return: Resource type
    :rtype: str
    """
    tags=[NUMERICALDATA_TAG,INSTRUMENT_TAG,OBSERVATORY_TAG,PERSON_TAG]
    for t in tags:
      ts=self.tree.xpath("/abc:{}/abc:{}".format(SPASE_TAG,t),namespaces=self.nsmap)
      if len(ts)!=0:
        return t
    return None
  def resource_id(self):
    """Get resource id

    :return: resource id
    :rtype: str
    """
    return self.tree.xpath("/abc:{}/*/abc:{}".format(SPASE_TAG,RESOURCEID_TAG), namespaces=self.nsmap)[0].text
  def set_resource_id(self, rid):
    """Set resource id

    :param rid: resource id value
    :type rid: str
    """
    self.tree.xpath("/abc:{}/*/abc:{}".format(SPASE_TAG,RESOURCEID_TAG), namespaces=self.nsmap)[0].text=rid
  def write(self, filename):
    """Save resource to file
    
    :param filename: filename
    :type filename: str
    """
    self.tree.write(filename, xml_declaration=True, encoding="utf-8", pretty_print=True)
  def is_type(self, rtype):
    """Check if object is of type :data:`rtype`

    :param rtype: desired type
    :type rtype: str
    :return: True if current object is of type :data:`rtype`, False otherwise
    :rtype: bool
    """
    p=self.tree.xpath("/abc:{}/abc:{}".format(SPASE_TAG,rtype),namespaces=self.nsmap)
    if len(p):
      return True
    return False
  def expected_filename(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    """Get the expected filename base on current objects resource id and repository root
    
    :param repository_root: path to the root directory of the SPASE resource repository, optional
    :type repository_root: str
    :return: expected filename
    :rtype: str
    """
    return SpaseManager.resource_id_to_path(self.resource_id(), repository_root)
  def iter_dependency(self):
    """Iterate over dependencies of the current object

    :return: SPASE address object 
    :rtype: amdapy.spase.SpaseAddr
    """
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
  def iter_contact(self):
    """Iterate over contact information

    :return: Contact information
    :rtype: amdapy.spase.SpaseContact
    """
    for e in self.tree.iter():
      if e.tag.endswith(CONTACT_TAG):
        yield Contact(e)
  def dirty_find(self, tag):
    """Temporary : find tag , ugly, ugly, ugly

    :param tag: tag we are looking for
    :type tag: str
    :return: First element with correponding tag
    :rtype: lxml.etree._Element
    """
    for e in self.tree.iter():
      if e.tag.endswith(tag):
        return e

class NumericalData(SpaseResource):
  """SPASE NumericalData interface class

  :param file: path to the resource file
  :type file: str
  """
  def __init__(self, file):
    """Object constructor
    """
    super(NumericalData,self).__init__(file)
  def iter_parameter(self):
    """Iterate over Parameter objects

    :return: Parameter objects defined in the current NumericalData file
    :rtype: amdapy.spase.Parameter
    """
    for p in self.tree.iter():
      if isinstance(p,etree._Element) and (not isinstance(p,etree._Comment)):
        if p.tag.endswith("Parameter"):
          yield Parameter(p)
  def iter_contact(self):
    """Iterate over contact information

    :return: contact information in the current NumericalData file
    :rtype: amdapy.spase.Contact
    """
    for p in self.tree.iter():
      if isinstance(p,etree._Element) and (not isinstance(p,etree._Comment)):
        if p.tag.endswith("Contact"):
          yield Contact(p)
  def parameter_count(self):
    """Count number of parameters

    :return: number of parameters defined in the current NumericalData file
    :rtype: int
    """
    return len([p for p in self.iter_parameter()])
  def contact_count(self):
    """Count contacts

    :return: number of contact object in the current object
    :rtype: int
    """
    return len([p for p in self.iter_contact()])
  def contains_parameter(self,param_id):
    """Check if the parameter :data:`param_id` exists

    :return: True if the current object contains the desired parameter, False otherwise
    :rtype: bool
    """
    for p in self.iter_parameter():
      if param_id==p.get_id():
        return True
    return False
  def check_resource_id(self, rid=None):
    """Check the validity of a resource id

    :param rid: resource id value, optional, if None then check current objects resource id
    :type rid: str
    :return: True if :data:`rid` is a valid resource id
    :rtype: bool
    """
    if rid is None:
      return self.resource_id().startswith(SPASE_ADDR_PREFIX)
    return rid.startswith(SPASE_ADDR_PREFIX)
  def check_filename(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    """Check that the filename and the resource id correspond

    :param repository_root: root of the SPASE resource repository
    :type repository_root: str
    :return: check that the resource id and the current file path correspond
    :rtype: bool
    """
    # get the expected path of the resource with current resource id.
    expected_path=self.expected_filename(repository_root)
    return expected_path==self.filename
  def remove_parameter(self, i):
    """Remove parameter

    :param i: index of the parameter
    :type i: int
    """
    if i<0:
      return
    if i>=self.parameter_count():
      return
    el=self.tree.xpath("/abc:Spase/abc:NumericalData", namespaces=self.nsmap)
    if len(el)==1:
      el[0].remove(self.get_parameter(i).root)
  def parameter_str(self, n_indent=0, repository_root=None):
    """Get summary of parameters as string

    :param n_indent: number of indentation characters to insert at each line, optional
    :type n_indent: int
    :param repository_root: root directory of the SPASE resource repository
    :type repository_root: str
    :return: string representation of the current objects parameters
    :rtype: str
    """
    a="{}Parameters :\n".format(n_indent*"\t")
    c=1
    for p in self.iter_parameter():
      a="{}{}{}. {}\n".format(a,"\t"*(n_indent+1),c,p.__str__())
      c=c+1
    return a
  def contact_str(self, n_indent=0, repository_root=None):
    """Get contact information string

    :param n_indent: number of indentation characters to insert at each line, optional, default is 0
    :type n_indent: int
    :param repository_root: root directory of the SPASE repository, optional
    :type repository_root: str
    :return: contact information string
    :rtype: str
    """
    a="{}Contact :\n".format(n_indent*"\t")
    c=1
    for p in self.iter_contact():
      a="{}{}{}. {}\n".format(a,"\t"*(n_indent+1),c,p.__str__(0,repository_root))
      c=c+1
    return a
  def add_parameter(self, param):
    """Add parameter to the current object

    :param param: parameter object
    :type param: amdapy.spase.Parameter
    """
    e=self.tree.xpath("/abc:Spase/abc:NumericalData", namespaces=self.nsmap)
    e[0].append(param)
  def __str__(self, repository_root=DEFAULT_REPOSITORY_ROOT):
    """NumericalData object string representation

    :param repository_root: root of the SPASE resource repository, optional
    :type repository_root: str
    :return: string representation of the NumericalData object
    :rtype: str
    """
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
  def get_parameter(self, i):
    """Get parameter at position :data:`i`

    :param i: parameter index
    :type i: int
    :return: None if index out of bounds, Parameter object otherwise
    :rtype: amdapy.spase.Parameter
    """
    if i>=self.parameter_count():
      return None
    c=0
    for p in self.iter_parameter():
      if c==i:
        return p
      c=c+1
  def get_contact(self, i):
    """Get contact element

    :param i: index of the contact
    :type i: int
    :return: None if :data:`i` is out of bounds, Contact information otherwise
    :rtype: amdapy.spase.Contact
    """
    if i>=self.contact_count():
      return None
    c=0
    for p in self.iter_contact():
      if c==i:
        return p
      c=c+1
  def get_instrument_id(self):
    """Get instrument id curresponding to the current resource

    :return: instrument resource id
    :rtype: str
    """
    el=self.tree.xpath("/abc:{}/abc:{}/abc:{}".format(SPASE_TAG,NUMERICALDATA_TAG,INSTRUMENTID_TAG),namespaces=self.nsmap)
    if len(el)==0:
      return SpaseAddr("")
    if len(el)>1:
      print("More then one instrument id tag found")
    return SpaseAddr(el[0].text)
  def get_mission_id(self):
    """Get mission id corresponding to the current resource

    :return: mission resource id
    :rtype: str
    """
    return None
  def add_contact(self, contact_el):
    """Add contact to current resource

    :param contact_el: contact information
    :type contact_el: amdapy.spase.Contact
    """
    # find the ResourceHeader element
    rh=None
    for e in self.tree.iter():
      if e.tag.endswith("ResourceHeader"):
        rh=e
    if e is None:
      return
    rh.append(contact_el)
  def remove_contact(self, i):
    """Remove contact information from current resource

    :param i: contact information element index
    :type i: int
    :return: None on failure
    :rtype: None
    """
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
  def get_description(self):
    """Get description of current object

    :return: object description string
    :rtype: str
    """
    desc_el=self.dirty_find("Description")
    return desc_el.text
  def set_description(self, description):
    """Set description of current object

    :param description: object description
    :type description: str
    """
    desc_el=self.dirty_find("Description")
    desc_el.text=description
  def get_measurement_type(self):
    """Get Measurement type of current object

    :return: object MeasurementType value
    :rtype: str
    """
    return self.dirty_find("MeasurementType").text
  def set_measurement_type(self, value):
    """Set MeasurementType value of the current object

    :param value: value
    :type value: str
    """
    el=self.dirty_find("MeasurementType")
    el.text=value
  def get_start_date(self):
    """Get current object start date

    :return: current object start date
    :rtype: datetime.datetime
    """
    sd_el=self.dirty_find("StartDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  def set_start_date(self, dt):
    """Set current object start date

    :param dt: start date
    :type dt: datetime.datetime
    """
    sd_el=self.dirty_find("StartDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  def get_stop_date(self):
    """Get current object stop date

    :return: stop
    :rtype: datetime.datetime
    """
    sd_el=self.dirty_find("StopDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  def set_stop_date(self, dt):
    """Set current object stop date

    :param dt: stop date
    :type dt: datetime.datetime
    """
    sd_el=self.dirty_find("StopDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  def get_release_date(self):
    """Get current object release date

    :return: release date
    :rtype: datetime.datetime
    """
    sd_el=self.dirty_find("ReleaseDate")
    if sd_el is None:
      return datetime.datetime()
    return datetime.datetime.strptime(sd_el.text, DATETIME_FORMAT)
  def set_release_date(self, dt):
    """Set current object release date

    :param dt: release date
    :type dt: datetime.datetime
    """
    sd_el=self.dirty_find("ReleaseDate")
    if isinstance(dt,datetime.datetime):
      sd_el.text=dt.strftime(DATETIME_FORMAT)
    else:
      sd_el.text=dt
  def get_cadence_min(self):
    """Get cadence min value

    :return: cadence min value
    :rtype: str
    """
    sd_el=self.dirty_find("CadenceMin")
    if sd_el is None:
      return None
    return sd_el.text
  def set_cadence_min(self, cadence):
    """Set current object min cadence value

    :param cadence: cadence minimum value
    :type cadence: str
    """
    sd_el=self.dirty_find("CadenceMin")
    sd_el.text=cadence
  def get_cadence_max(self):
    """Get cadence maximum value

    :return: cadence max
    :rtype: str
    """
    sd_el=self.dirty_find("CadenceMax")
    if sd_el is None:
      return None
    return sd_el.text
  def set_cadence_max(self, cadence):
    """Set cadence maximum value

    :param cadence: maximum cadence value
    :type cadence: str
    """
    sd_el=self.dirty_find("CadenceMax")
    sd_el.text=cadence
  def set_component_prefix(self, i, prefix):
    """Set component prefix 

    :param i; index of the parameter
    :type i: int
    :param prefix: prefix value
    :type prefix: str
    """
    # get the ith Parameter object
    parameter=self.get_parameter(i)
    if not parameter is None:
      if parameter.get_size()>1:
        parameter.set_component_prefix(prefix)
  def set_component_suffix(self, param_id, suffix):
    """Set component suffix

    :param param_id: parameter id
    :type param_id: str
    :param suffix: suffix value
    :type suffix: str
    """
    # get the ith parameter
    parameter=self.get_parameter(param_id)
    if not parameter is None:
      if parameter.get_size()>1:
        parameter.set_component_suffix(suffix)
    
class Instrument(SpaseResource):
  """Class for representing and modifying SPASE Instrument resources

  :param file: path to the resource file
  :type file: str
  """
  def __init__(self, file):
    """Object constructor
    """
    super(Instrument,self).__init__(file)

class Observatory(SpaseResource):
  """Class for representing and modifying SPASE Observatory resources

  :param file: path to the resource file
  :type file: str
  """
  def __init__(self, file):
    """Object constructor
    """
    super(Observatory,self).__init__(file)

class Person(SpaseResource):
  """Class for representing SPASE Person resource

  :param file: path to the resource file
  :type file: str
  """
  def __init__(self, file):
    """Object constructor
    """
    super(Person,self).__init__(file)

class XMLElement:
  """Class for representing an XML element

  :param element: root element of the object
  :type element: lxml.etree._Element
  """
  def __init__(self, element):
    """Object constructor
    """
    ## root XML element.
    self.root=element
    ## XML namespace mapping.
    self.nsmap=element.nsmap
    if None in self.nsmap:
      self.nsmap["abc"]=self.nsmap[None]
      del self.nsmap[None]
  def find(self, tag):
    """Find element by tag

    :param tag: tag of the desired element
    :type tag: str
    :return: element object if found, None otherwise
    :rtype: lxml.etree._Element or None
    """
    for e in self.root.iter():
      if isinstance(e,etree._Comment):
        continue
      if e.tag.endswith(tag):
        return e
    return self.root.find("abc:{}".format(tag),namespaces=self.nsmap)

class Element(XMLElement):
  """Class represent Element tags in multidimensional timeseries SPASE parameters

  :param el: xml element 
  :type el: lxml.etree._Element
  """
  def __init__(self, el):
    """Object constructor
    """
    super(Element,self).__init__(el)
    ## Name of the Element
    self.name=self.get_name()
    ## Key of the Element
    self.key=self.get_key()
    ## Index of the Element
    self.index=self.get_index()
  def get_name(self):
    """Get element name

    :return: element name
    :rtype: str
    """
    return self.find(NAME_TAG).text
  def set_name(self, name):
    """Set element name

    :param name: name
    :type name: str
    """
    name_el=self.find(NAME_TAG)
    name_el.text=name
  def get_index(self):
    """Get element index

    :return: element index
    :rtype: int
    """
    return self.find(INDEX_TAG).text
  def get_key(self):
    """Get element key

    :return: key
    :rtype: str
    """
    return self.find(PARAMETERKEY_TAG).text
  def __str__(self, n_indent=0):
    """Element string representation

    :param n_indent: number of indentation characters to insert at each line
    :type n_indent: int
    :return: object string representation
    :rtype: str
    """
    return "{}Component(key:{},name:{},i:{})".format(n_indent*"\t",self.key, self.name, self.index)

  
class Contact(XMLElement):
  """Class for representing SPASE Contact resources

  :param element: xml element from which contact is defined
  :type element: lxml.etree._Element
  """
  def __init__(self, element):
    """Object constructor
    """
    super(Contact,self).__init__(element)
  def __str__(self, n_indent=0, repository_root=None):
    """Contact string representation

    :param n_indent: number of indentation characters to insert a each line
    :type n_indent: int
    :param repository_root: root path of the SPASE repository
    :type repository_root: str
    """
    if repository_root is None:
      return "{}Contact(id:{},role:{})".format(n_indent*"\t",self.person_id(),self.role())
    person_id=self.person_id()
    if not person_id.is_valid():
      return strcol(self.__str__(n_indent=n_indent), "r")
    person_path=SpaseManager.resource_id_to_path(person_id,repository_root)
    if not os.path.exists(person_path):
      return strcol(self.__str__(n_indent=n_indent), "r")
    return strcol(self.__str__(n_indent=n_indent),"g")
  def person_id(self):
    """Get person id

    :return: Person id value
    :rtype: str
    """
    return SpaseAddr(self.find(PERSONID_TAG).text)
  def role(self):
    """Get person role

    :return: role
    :rtype: str
    """
    return self.find(ROLE_TAG).text
  def make_contact_xmlel(person_id, role="GeneralContact"):
    """Make a Contact element

    :param person_id: person id
    :type person_id: str
    :param role: role
    :type role: str
    :return: Contact XML element
    :rtype: lxml.etree._Element
    """
    contact_el=etree.Element("Contact")
    pid_el=etree.Element("PersonID")
    pid_el.text=person_id
    role_el=etree.Element("Role")
    role_el.text=role
    contact_el.append(pid_el)
    contact_el.append(role_el)
    return contact_el

class Parameter(XMLElement):
  """Class for representing parameters in the SPASE resource context

  :param parameter_element: parameter XML element
  :type parameter_element: lxml.etree._Element
  """
  def __init__(self, parameter_element):
    """Object constructor
    """
    super(Parameter,self).__init__(parameter_element)
  def get_id(self):
    """Get parameter id

    :return: parameter id
    :rtype: str
    """
    paramkey_el=self.find("ParameterKey")
    if not paramkey_el is None:
      return paramkey_el.text
    return None
  def get_name(self):
    """Get parameter name

    :return: parameter name
    :rtype: str
    """
    paramname_el=self.find("Name")
    if not paramname_el is None:
      return paramname_el.text
    return None
  def get_ucd(self):
    """Get ucd

    :return: UCD value
    :rtype: str
    """
    el=self.find("Ucd")
    if el is None:
      return None
    return el.text
  def get_units(self):
    """Get units

    :return: units
    :rtype: str
    """
    el=self.find("Units")
    if not el is None:
      return el.text
    return None
  def get_size(self):
    """Get size

    :return: parameter size
    :rtype: tuple ints
    """
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
  def valid(self):
    """Check if parameter definition is valid

    :return: True is current parameter definition is valid, False otherwise
    :rtype: bool
    """
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
  def iter_component(self):
    """Iterate over components

    :return: components
    :rtype: amdapy.spase.Element
    """
    if self.get_size()>1:
      struct_el=self.find(STRUCTURE_TAG)
      for e in struct_el.iter():
        if isinstance(e, etree._Comment):
          continue
        if e.tag.endswith(ELEMENT_TAG):
          yield Element(e)
  def component(self,i):
    """Get component by index

    :param i: component index
    :type i: int
    :return: i-th component
    :rtype: amdapy.spase.Element
    """
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
  def component_name(self,i):
    """Get i-th components name

    :param i: component index
    :type i: int
    :return: i-th component name
    :rtype: str
    """
    if i<0 or i>=self.get_size():
      return None
    el=self.component(i)
    return el.name
  def __str__(self,n_indent=0):
    """Parameter string representation

    :param n_indent: number of indentation characters inserted at each line
    :type n_indent: int
    :return: parameters string representation
    :rtype: str
    """
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
  def get_component_prefix(self):
    """Get component prefix

    :return: component prefix
    :rtype: str
    """
    #print("in Parameter.get_component_prefix : self.size={}".format(self.get_size()))
    #print("self.component_count/count_element : {}".format(self.count_elements()))
    if self.get_size()==1:
      return None
    if self.count_elements()==0:
      return None
    # iterate over components.
    component_names=[c.name for c in self.iter_component()]
    return self.get_similar_prefix(np.array(component_names,dtype=object))
  def set_component_prefix(self, prefix):
    """Set component prefix

    :param prefix: prefix
    :type prefix: str
    """
    if self.get_size()!=1:
      # get the current prefix value
      old_prefix=self.get_component_prefix()
      if len(old_prefix):
        for component in self.iter_component():
          # get component name
          cname=component.name
          newcname="{}{}".format(prefix,cname[len(old_prefix):])
          component.set_name(newcname)
  def get_component_suffix(self):
    """Get component suffix

    :return: component suffix
    :rtype: str
    """
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
  def set_component_suffix(self,scheme):
    """Set component suffix

    :param scheme: suffix scheme
    :type scheme: str
    """
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
  def get_similar_prefix(self,name_list, n=None):
    """Get similar prefix : this function is temporary and should be changes

    :param name_list: list of parameter names
    :type name_list: list of str
    :param n: ?? number of parameters
    :param n: int
    :return: similar prefix
    :rtype: str
    """
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
  def count_elements(self):
    """Get element count

    :return: element count
    :rtype: int
    """
    c=0
    for e in self.root.iter():
      if isinstance(e, etree._Comment):
        continue
      if e.tag.endswith("Element"):
        c=c+1
    return c
  def numericaldata_empty__str__(self):
    """Numerical data empty string

    :return: numerical data empty string ??
    :rtype: str
    """
    if self.valid():
      return Fore.GREEN+"Parameter (id:{}, name:{}, units:{}, size:{})".format(self.get_id(), self.get_name(),self.get_units(), self.get_size())+Style.RESET_ALL
    return Fore.RED+"Parameter (id:{}, name:{}, units:{}, size:{})".format(self.get_id(), self.get_name(),self.get_units(), self.get_size())+Style.RESET_ALL
  @staticmethod
  def make_parameter_xmlel(name, key, size=1, component_prefix="u", rhint="TimeSeries"):
    """Make a parameter XML element

    :param name: name of the parameter
    :type name: str
    :param key: parameter key
    :type key: str
    :param size: size of the parameter
    :type size: int or tuple ints
    :param component_prefix: prefix to give to the components
    :type component_prefix: str
    :param rhint: display type
    :type rhint: str
    :return: parameter XML element
    :rtype: lxml.etree._Element
    """
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
  @staticmethod
  def make_structure_xmlel(size, name_prefix="u", parameter_key=""):
    """Make structure XML element

    :param size: size
    :type size: int
    :param name_prefix: component name prefix
    :type name_prefix: str
    :param parameter_key: parameter key
    :type parameter_key: str
    :return: component element
    :rtype: lxml.etree._Element
    """
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
  def get_display_type(self):
    """Get display type

    :return: parameter display type
    :rtype: str
    """
    e=self.find("DisplayType")
    if e is None:
      return None
    return e.text
  def set_display_type(self,value):
    """Set display type

    :param value: display type value
    :type value: str
    """
    e=self.find("DisplayType")
    if not e is None:
      e.text=value
  def has_coordinate_system(self):
    """Check if parameter has a coordinate system

    :return: True if found a CoordinateSystem element, False otherwise
    :rtype: bool
    """
    el=self.find(COORDINATESYSTEM_TAG)
    if el is None:
      return False
    return True
  def get_coordinate_system_name(self):
    """Get coordinate system name

    :return: Coordinate system name
    :rtype: str
    """
    el=self.find(COORDINATESYSTEMNAME_TAG)
    if el is None:
      return None
    return el.text

class SpaseManager:
  """Class for managing SPASE resources

  :param root: root of the repository
  :type root: str
  """
  def __init__(self, root):
    """Object constructor
    """
    ## Root of the repository.
    self.root=root
  def iter_xml_file_path(self,path=None):
    """Iterate over all XML files under repository root directory

    :param path: path to walk, default is None and walks the default root directory
    :type path: str or None
    :return: path to XML files
    :rtype: str
    """
    if path is None:
      for p in self.iter_xml_file_path(path=self.root):
        yield p
    else:
      for root,dirs,files in os.walk(path):
        for f in files:
          if f.endswith(".xml"):
            yield os.path.join(root,f)
  def iter_resource(self, rtype=None):
    """Iterate over SPASE resource files

    :param rtype: resource type
    :type rtype: str
    :return: resources
    :rtype: amda.spase.SpaseResource
    """
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
  def iter_numerical_data(self):
    """Iterate numerical data resources

    :return: NumercialData resouces
    :rtype: amdapy.spase.NumericalData
    """
    for r in self.iter_resource(rtype=NUMERICALDATA_TYPE):
      yield NumericalData(r.filename)
  def iter_instrument(self):
    """Iterate Instrument resources

    :return: Instrument resources
    :rtype: amdapy.spase.Instrument
    """
    for r in self.iter_resource(rtype=INSTRUMENT_TYPE):
      yield Instrument(r.filename)
  def iter_observatory(self):
    """Iterate Observatory resources

    :return: Observatory resources
    :rtype: amdapy.spase.Observatory
    """
    for r in self.iter_resource(rtype=OBSERVATORY_TYPE):
      yield Observatory(r.filename)
  def iter_person(self):
    """Iterate Person resources

    :return: Person resources
    :rtype: amdapy.spase.Person
    """
    for r in self.iter_resource(rtype=PERSON_TYPE):
      yield Person(r.filename)
  def health_check(self):
    """Check the health of the repository
    """
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
  def get_duplicate_ids(self):
    """Get list of resources with duplicated ids

    :return: dictionary indexed by resource id encountered more then once, and with values a list of files having the corresponding id.
    :rtype: dict
    """
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
  def get_resource_by_id(self, res_id):
    """Get a resource by id
    
    :param res_id: resource id
    :type res_id: str
    :return: list of resource objects with corresponding id
    :rtype: list
    """
    a=[]
    for res in self.iter_resource():
      if res.resource_id()==res_id:
        a.append(res)
    return a
  @staticmethod
  def resource_id_to_path(res_id, repository_root):
    """Get absolute path of the spase resource file

    :param res_id: resource id
    :type res_id: str
    :param repository_root: root directory of the SPASE repository
    :type repository_root: str
    """
    t=res_id.replace(SPASE_ADDR_PREFIX, "")
    return os.path.join(repository_root, "{}.xml".format(t))
  @staticmethod
  def path_to_resource_id(path, repository_root):
    """Get resource id corresponding to a given path

    :param path: path
    :type path: str
    :param repository_root: repository root directory
    :type repository_root: str
    :return: resource id corresponding to :data:`path`
    :rtype: str
    """
    t=path.replace(repository_root, "")
    if t.startswith("/"):
      t=t[1:]
    return "{}{}".format(SPASE_ADDR_PREFIX, t.replace(".xml",""))
  def get_bad_ids(self):
    """Check for all badly ided resources and return the list

    :return: list of pairs (path, id) 
    :rtype: list
    """
    a=[]
    for r in self.iter_resource():
      path=r.filename
      id_=r.resource_id()
      id_path=self.resource_id_to_path(id_)
      if path!=id_path:
        a.append((path, id_))
    return a
  def find_resource(self,name):
    """Find resource by filename

    :param name: name of the resource file
    :type name: str
    :return: Spase resource if found None otherwise
    :rtype: amdapy.spase.SpaseResource
    """
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

def get_cmd_output(cmd):
  """Run a command and get output

  :param cmd: command
  :type cmd: str
  :return: output
  :rtype: str
  """
  os.system("{} > temp.output".format(cmd))
  a=""
  with open("temp.output","r") as f:
    a=f.read()
    f.close()
  os.system("rm temp.output")
  return a

     
def parse_args():
  """Parse command line args

  :return: command line arguments
  :rtype: argparse.Arguments
  """
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

def rtype_from_args(args):
  """Get list of resource types from args

  :return: list of types
  :rtype: list
  """
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
