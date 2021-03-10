"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: pds.py
:brief: Classes and functions for managing access to data stored by PDS

"""
import numpy as np
import datetime

from amdapy.str_utils import *

## PDS ASCII file tags
PDS_END_TAG="END"
NEWLINE="\n"
ASSIGNMENT="="
STRBEG="\""

PDS_DATETIME="TIME"
PDS_DATETIME_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"
PDS_FLOAT="ASCII_REAL"
PDS_INT="ASCII_INTEGER"
PDS_FIELD_NAME="NAME"
PDS_FIELD_COLNUM="COLUMN_NUMBER"
PDS_FIELD_UNIT="UNIT"
PDS_FIELD_DATATYPE="DATA_TYPE"
PDS_FIELD_FILLVAL="MISSING_CONSTANT"

PDS_ERR_MISSING_LABEL_FILE=2
PDS_ERR_MISSING_DATA_FILE=3

## PDSObject class documentation.
#
#  This class is used to represent the PDS label objects.
class PDSObject:
  """PDSObject class definition. This is the base class for representing PDS ASCII header data

  :param name: name of the object
  :type name: str
  :param value: value of the parameter
  :type value: ?
  """
  def __init__(self,name=None,value=None):
    """Object initialization
    """
    ## Object name.
    self.name=name
    ## Object value.
    self.value=value
  def summary(self):
    """Print summary of current object
    """
    if self.is_attribute():
      print("Attribute {} : {}".format(self.name, self.value))
    else:
      print("Object type : ", self.name)
      for child in self.value:
        print(child)
  def get(self, name):
    """Get object attribute by name

    :param name: name of the desired attribute
    :type name: str
    :return: value of the attribute corresponding to :data:`name`
    :rtype: value type
    """
    if self.is_object():
      for c in self.iter():
        if c.is_attribute():
          if c.name==name:
            return c.value
  def type(self):
    """Get type of current PDSObject

    :return: type of the current object
    :rtype: str
    """
    if self.is_object():
      return self.name
    return "att"
  def is_type(self,t):
    """Check if object is of type :data:`type`

    :param t: type
    :type t: str
    :return: True if current object is of type :data:`t`, False otherwise
    :rtype: bool
    """
    return self.name==t
  def is_attribute(self):
    """Check if current object is an attribute
    
    :return: True is current object is an attribute, False otherwise
    :rtype: bool
    """
    return isinstance(self.name, str) and isinstance(self.value, str)
  def is_object(self,t=None):
    """Check if current object is an PDS Object.

    :param t: type, optional
    :type t: str
    :return: True is current object is a PDS Object, False otherwise
    :rtype: boolA
    """
    if t is None:
      return isinstance(self.name, str) and isinstance(self.value, list)
    return isinstance(self.name, str) and isinstance(self.value, list) and self.name==t
  def valid(self):
    """Check if the current object is valid

    :return: True if object is valid, False otherwise
    :rtype: bool
    """
    if self.is_attribute():
      return not len(self.name)==0 and not len(self.value)==0
    else:
      for att in self.value:
        if not att.valid():
          return False
      return self.has_end() 
  def has_end(self):
    """Check if the current object has an end tag.

    :return: True if current object has an end tag, False otherwise
    :rtype: bool
    """
    if self.is_attribute():
      return True
    for att in self.value:
      if att.name=="END_OBJECT" and att.value==self.name:
        return True
    return False
  @staticmethod
  def next(self,input_str):
    """Parse next PDSObject

    :param input_str: input that we want to parse
    :type input_str: str
    :return: next available PDSOject and rest of string to be parsed
    :rtype: tuple (amdapy.pds.PDSObject, str)
    """
    return PDSObject(),input_str
  def __str__(self,n_indent=0):
    """String representation of the current object

    :param n_indent: number of indentation characters that will be inserted in front of each line
    :type n_indent: int
    :return: string representation of the current object
    :rtype: str
    """
    a="{}PDSObject(name={},value={})".format(n_indent*"\t",self.name,self.value)
    for att in self.value:
      a=a+"\n"+att.__str__(n_indent=n_indent+1)
    return a
  def add_attribute(self,attribute):
    """Add attribute to current object

    :param attribute: attribute we wish to add.
    :type attribute: amdapy.pds.PDSAttribute
    """
    self.value.append(attribute)
  def iter_object(self,t=None):
    """Iterator over PDSOjects

    :param t: type of object, optional, default behaviour iterates over all objects
    :type t: str
    :return: yields all PDSObject objects
    :rtype: amdapy.pds.PDSObject
    """
    if self.is_object():
      for o in self.value:
        if o.is_object(t):
          if t is None:
            yield o
          else:
            if o.is_type(t):
              yield o
          for so in o.iter_object(t):
            yield so
  def iter(self):
    """Iterate over children
    """
    if self.is_object():
      for child in self.value:
        yield child
  def iter_attribute(self):
    """Iterate over current object attributes

    :return: current object attributes
    :rtype: amdapy.pds.PDSAttribute
    """
    if self.is_object():
      for c in self.iter():
        if c.is_attribute():
          yield c

class PDSAttribute(PDSObject):
  """Base class for representing PDS ASCII dataset header attributes
  
  :param name: name of the attribute, optional , default is None
  :type name: None or str
  :param value: value of the attribute
  :type value: value type
  """
  def __init__(self,name=None,value=None):
    """Object constructor
    """
    ## Attribute name.
    self.name=name
    ## Attribute value.
    self.value=value
  def summary(self):
    """Print summary of current object
    """
    print("attribute : ", self.name, self.value)
  def valid(self):
    """Check if current attribute is valid
    
    :return: True is the attribute is valid (:data:`name` and :data:`value` are not None)
    :rtype: bool
    """
    if self.name==PDS_END_TAG:
      return True
    return not self.name is None and not self.value is None
  def is_equal(self,attr):
    """Check equality between current attribute and another

    :param attr: other attribute to compare with
    :type attr: amdapy.pds.PDSAttribute
    :return: True if both attributes have same name and value, False otherwise
    :rtype: bool
    """
    return attr.name==self.name and attr.value==self.value
  def __str__(self,n_indent=0):
    """String representation of the current object

    :param n_indent: number of indentation characters that will be added to begining of each line, optional, default is 0
    :type n_indent: int
    """
    return "{}PDSAttribute(name={},value={})".format(n_indent*"\t",self.name,self.value)
  @staticmethod
  def fromstring(in_str):
    """Get an attribute from string input

    :param in_str: input string that we want to parse
    :type in_str: str
    :return: New attribute if valid, None otherwise
    :rtype: None or amdapy.pds.PDSAttribute
    """
    if ASSIGNMENT in in_str:
      as_pos=in_str.find(ASSIGNMENT)
      name=in_str[:as_pos]
      val=in_str[as_pos+1:]
      name=str_rem_ends(name)
      val=str_rem_ends(val)
      if "\"" in val:
        #val=val.replace("\n"," ")
        val=str_rem_successive(val)
        val=str_rem_ends(val)
      return PDSAttribute(name, val)
    return PDSAttribute()
  @staticmethod
  def next(in_str):
    """Parse next PDSAttributre object from string

    :param in_str: input string we wish to parse
    :type in_str: str
    :return: next object if valid, None otherwise
    :rtype: amdapy.pds.PDSAttribute
    """
    # get position of next line and next assignment
    nl_pos=in_str.find(NEWLINE)
    as_pos=in_str.find(ASSIGNMENT)
    # if no newline
    if nl_pos<0:
      # if there is an assignment
      return PDSAttribute.fromstring(in_str),""
    # get the first line of input data
    line=in_str[:nl_pos]
    if as_pos<0:
      # if there are no assignments
      return PDSAttribute.fromstring(line),in_str[nl_pos+1:]
    if as_pos<nl_pos:
      # if first line contains an assignment
      if in_str[as_pos+2]=="\"":
        # assigning a string value, line ends at second occurence of "
        val_beg=in_str.find("\"")
        line_end=in_str.find("\"",val_beg+1)+1
        line=in_str[:line_end]
        return PDSAttribute.fromstring(line), in_str[line_end:]
      elif in_str[as_pos+2]=="(":
        line_end=in_str.find(")")+1
        line=in_str[:line_end]
        return PDSAttribute.fromstring(line),in_str[line_end:]
      else:
        return PDSAttribute.fromstring(line),in_str[nl_pos+1:]
    else:
      return PDSAttribute.fromstring(line),in_str[nl_pos+1:]

class PDSLabel:
  """Container class for PDSLabel objects

  :param label_filename: path to the PDS dataset label file
  :type label_filename: str
  """
  def __init__(self,label_filename):
    """Object constructor
    """
    self.data=None
    self.parse(label_filename)
    self.column_index_map={}
    self.set_column_index_map()
  def set_column_index_map(self):
    """Set the mapping between desired column names to the original column names
    """
    prev_index=0
    for o in self.iter_column():
      temp_name=o.get("NAME")
      temp_items=o.get("ITEMS")
      if not temp_items is None:
        temp_items=int(temp_items)
        self.column_index_map[temp_name]=[prev_index+i for i in range(temp_items)]
        prev_index=1+self.column_index_map[temp_name][-1]
      else:
        self.column_index_map[temp_name]=prev_index
        prev_index=prev_index+1
  def summary(self):
    """Print summary of the current object
    """
    print("PDS Label file")
    print("columns : ", self.column_count())
    for c in self.iter_column():
      print("\tcolumn : ",c.get("NAME"))
  def column_count(self):
    """Count the column objects

    :return: number of column objects
    :rtype: int
    """
    count=0
    for c in self.iter_object("COLUMN"):
      count=count+1
    return count
  def iter_object(self, t=None):
    """Iterator over objects

    :param t: desired object type
    :type t: str
    :return: objects of the desired type, default is to yield all objects
    :rtype: amdapy.pds.PDSObject
    """
    for o in self.data:
      if o.is_object():
        if t is None:
          yield o
        else:
          if o.is_type(t):
            yield o
        for so in o.iter_object(t):
          yield so
  def parse(self, filename):
    """Parse a PDS label file

    :param filename: path to the label filename
    :type filename: str
    :return: PDSLabel object
    :rtype: amdapy.pds.PDSLabel
    """
    s=readfile(filename)
    self.data=[]
    while len(s):
      obj, s=self.next(s) 
      if obj.valid():
        self.data.append(obj)
  def iter_column(self):
    """Iterate over column objects

    :return: columns objects
    :rtype: amdapy.pds.PDSObject
    """
    for c in self.iter_object("COLUMN"):
      yield c
  def next(self,in_str):
    """Parse new PDS label file object
    
    :param in_str: string we wish to parse
    :type in_str: str
    :return: next PDSObject
    :rtype: amdapy.pds.PDSObject
    """
    # first get next PDSAttribute object
    obj, s=PDSAttribute.next(in_str)
    if obj.name=="OBJECT":
      no=PDSObject(name=obj.value,value=[])
      while not no.valid() and len(s):
        obj,s=self.next(s)
        if obj.valid():
          no.add_attribute(obj)
      return no,s
    return obj,s
  def find_column_by_name(self,col_name):
    """Find a column by name
    
    :param col_name: name of the column
    :type col_name: str
    :return: Column object is exists, None otherwise
    :rtype: PDSObject or None
    """

    for col in self.iter_column():
      if col.get("NAME")==col_name:
        return col

class PDSDataset:
  """PDSDataset documentation. This is the class we use to interface with PDS ASCII datasets.

  :param label_filename: path the the PDS ASCII label file
  :type label_filename: str
  :param data_filename: path to the PDS ASCII table file
  :type data_filename: str
  :param table_sep: separation character used in the table file, optional, default is space
  :type table_sep: str
  """
  def __init__(self,label_filename="", data_filename="", table_sep=","):
    """Object constructor
    """
    ## Path to the label file.
    self.label_filename=label_filename
    ## Path to the data file.
    self.data_filename=data_filename
    ## Data container.
    self.data=None
    self.load_data(data_filename,sep=table_sep)
    ## Label data.
    self.label_data=PDSLabel(label_filename=label_filename)
  def summary(self):
    """Print dataset summary
    """
    print("Label filename : {}".format(self.label_filename))
    print("Data filename  : {}".format(self.data_filename))
    print("Data shape     : {}".format(self.shape()))
    print("")
    print("Columns :")
    for col in self.columns():
      if not col is None:
        col_name=col.get(PDS_FIELD_NAME)
        datatype=self.column_datatype(col_name)
        ind=self.label_data.column_index_map[col_name]
        t_data=self.column_data(col_name)
        print(" {}. {}, {}, {}".format(ind,col_name,datatype,t_data.shape))
  def load_data(self,filename,sep=","):
    """Load contents of the dataset from files

    :param filename: path of the data file
    :type filename: str
    :param sep: separation character, optional, default is space
    :type sep: str
    """
    # load data from csv type file, separation characters are spaces
    self.data=readfile(filename)
    self.data=np.array([list(filter(None,l.split(sep))) for l in self.data.split(NEWLINE) if len(l)], dtype=object)
  def shape(self):
    """Get dataset shape
    
    :return: shape of the dataset data
    :rtype: tuple of ints
    """
    return len(self.data), len(self.data[0])
  def columns(self):
    """Iterator over columns

    :return: columns objects
    :rtype: amdapy.pds.PDSObject
    """
    # get columns index
    for col in self.label_data.iter_column():
      if not col is None:
        yield col
  def datetime_str_to_float(self,dt_str,scheme=PDS_DATETIME_FORMAT):
    """Convert a string timestamp to datetime

    :param dt_str: timestamp string
    :type dt_str: str
    :param scheme: formating string (as used by datetime.strptime)
    :type scheme: str
    :return: datetime object corresponding to input timestamp
    :rtype: datetime.datetime
    """
    e=datetime.datetime.utcfromtimestamp(0)
    try:
      dt=datetime.datetime.strptime(dt_str,scheme)
    except:
      return None
    tts=(dt-e).total_seconds()
    return tts
  def column_data(self,col_name):
    """Get column data

    :param col_name: name of the column whose data we want
    :type col_name: str
    :return: :data:`col_name` data, or None if column does not exist
    :rtype: None or numpy.array
    """
    dt=self.column_datatype(col_name)
    if dt=="TIME":
      t=[self.datetime_str_to_float(k) for k in self.data[:,self.column_index(col_name)]]
      return np.array(t,dtype=np.float64)
    if not dt is None:
      col=self.label_data.find_column_by_name(col_name)
      missing_constant=col.get("MISSING_CONSTANT")
      temp_data=self.data[:,self.column_index(col_name)]
      if len(temp_data.shape)==1:
        for i in range(len(temp_data)):
          if temp_data[i]==missing_constant:
            temp_data[i]="nan"
          # try converting value to float, if cannot then replace value by nan
          try:
            fv=np.array(temp_data[i],dtype=dt)
          except:
            print("Unable to convert value {} to type np.float64".format(temp_data[i]))
            temp_data[i]="nan"
      return np.array(temp_data, dtype=self.column_datatype(col_name))
    return self.data[:,self.column_index(col_name)]
  def column_datatype(self,col_name):
    """Get column datatype

    :param col_name: column name
    :type col_name: str
    :return: datatype associated with the column
    :rtype: type
    """
    col=self.label_data.find_column_by_name(col_name)
    dt_str=col.get(PDS_FIELD_DATATYPE).replace("\"","")
    if dt_str==PDS_FLOAT:
      return np.float64
    if dt_str==PDS_INT:
      return np.intc    
    if dt_str==PDS_DATETIME:
      return "TIME"
    print("WARNING : datatype could not be found : " , dt_str)
  def column_index(self,col_name):
    """Get column index, if column has multiple dimensions then return a list of indexes

    :param col_name: name of the column
    :type col_name: str
    :return: index of the column or None if column :data:`col_name` does not exist
    :rtype: int
    """
    return self.label_data.column_index_map[col_name]
    for col in self.label_data.iter_column():
      if col.get("NAME")==col_name:
        items_att=col.get("ITEMS")
        if not items_att is None:
          first_index=int(col.get("COLUMN_NUMBER"))-1
          return [first_index+i for i in range(int(items_att))]
        return int(col.get("COLUMN_NUMBER"))-1
  def column_name_by_index(self,index):
    """Get column name from index

    :param index: index
    :type index: int
    :return: :data:`index`-th columns name
    :rtype: str
    """
    for c in self.column_names():
      ind=self.column_index(c)
      if ind==index:
        return c
  def column_names(self):
    """Iterate over column names

    :return: column names
    :rtype: str
    """
    for c in self.columns():
      yield c.get(PDS_FIELD_NAME)
  def has_column(self, col_name):
    """Check if dataset contains column named :data:`col_name`

    :param col_name: column name
    :type col_name: str
    :return: True is current dataset contains a column named :data:`col_name`, False otherwise
    :rtype: bool
    """
    for c in self.column_names():
      if c == col_name:
        return True
    return False
  def time_column_name(self):
    """Get the name of the column containing Time data

    :return: column name
    :rtype: str
    """
    for c in self.column_names():
      if "time" in c.lower():
        return c
    return None
  def time_data(self):
    """Get the Time data

    :return: time data array
    :rtype: numpy.array
    """
    time_col_name=self.time_column_name()
    if time_col_name is None:
      return np.array()
    return self.column_data(time_col_name)
  def timespan(self):
    t=self.time_data()
    return t[0],t[-1]


