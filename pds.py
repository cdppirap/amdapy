## Read a PDS ASCII file
#
#  Read a PDS ASCII file
#  @file pds.py
#  @author Alexandre Schulz
#  @brief Sorry for the horrible coding.
import numpy as np
import datetime

from str_utils import *

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
  ## PDSObject.__init__
  #
  #  Initialize a PDSObject.
  #  @param self object pointer.
  #  @param name (str) name of the object.
  #  @param value (string) value of the object.
  def __init__(self,name=None,value=None):
    ## Object name.
    self.name=name
    ## Object value.
    self.value=value
  ## PDSObject.summary
  #
  #  Print object summary.
  #  @param self object pointer.
  def summary(self):
    if self.is_attribute():
      print("Attribute {} : {}".format(self.name, self.value))
    else:
      print("Object type : ", self.name)
      for child in self.value:
        print(child)
  ## PDSObject.get
  #
  #  Get one of the object attributes.
  #  @param self object pointer.
  #  @param name attribute name.
  def get(self, name):
    if self.is_object():
      for c in self.iter():
        if c.is_attribute():
          if c.name==name:
            return c.value
  ## PDSObject.type
  #
  #  Get the current object type.
  #  @param self object pointer.
  def type(self):
    if self.is_object():
      return self.name
    return "att"
  ## PDSObject.is_type
  #
  #  Check if the current object is of the chosen type.
  #  @param self object pointer.
  #  @param self t object type.
  #  @return bool True if current object is of type <type>, False otherwise.
  def is_type(self,t):
    return self.name==t
  ## PDSObject.is_attribute
  #
  #  Check if the current object is an attribute.
  #  @param self object pointer.
  #  @return bool True is current object is an attribute, False otherwise.
  def is_attribute(self):
    return isinstance(self.name, str) and isinstance(self.value, str)
  ## PDSObject.is_object
  #
  #  Check if current object is a PDS  object.
  #  @param self object pointer.
  #  @param t (default : None) object type.
  #  @return bool True is current object is a PDS object, False otherwise. If t isn't None than return True only if the current object type matches.
  def is_object(self,t=None):
    if t is None:
      return isinstance(self.name, str) and isinstance(self.value, list)
    return isinstance(self.name, str) and isinstance(self.value, list) and self.name==t
  ## PDSOobject.valid
  #
  #  Check if the current object is a valid PDS object.
  #  @param self object pointer.
  #  @return bool check if current object is a valid PDS object.
  def valid(self):
    if self.is_attribute():
      return not len(self.name)==0 and not len(self.value)==0
    else:
      for att in self.value:
        if not att.valid():
          return False
      return self.has_end() 
  ## PDSObject.has_end
  #
  #  Check that the current object contains an END tag.
  #  @param self object pointer.
  #  @return bool current object contains a matching END tag.
  def has_end(self):
    if self.is_attribute():
      return True
    for att in self.value:
      if att.name=="END_OBJECT" and att.value==self.name:
        return True
    return False
  ## PDSObject.next
  #
  #  Parse the next PDS object.
  #  @param self object pointer.
  #  @param input_str string to be parsed.
  #  @return next PDS object.
  @staticmethod
  def next(self,input_str):
    return PDSObject(),input_str
  ## PDSObject.__str__
  #
  #  PDSObject string representation.
  #  @param self object pointer.
  #  @param n_indent (int, default:0) number of indentation characters to insert at begining of each line.
  #  @return str string representation of the current object.
  def __str__(self,n_indent=0):
    a="{}PDSObject(name={},value={})".format(n_indent*"\t",self.name,self.value)
    for att in self.value:
      a=a+"\n"+att.__str__(n_indent=n_indent+1)
    return a
  ## PDSObject.add_attribute
  #
  #  Add an attribute to the current object.
  #  @param self object pointer.
  #  @param attribute attribute object.
  def add_attribute(self,attribute):
    self.value.append(attribute)
  ## PDSObject.iter_object
  #
  #  Iterate over the current objects children.
  #  @param self object pointer.
  #  @param t yield only object of type <t>
  #  @return yield object.
  def iter_object(self,t=None):
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
  ## PDSObjeect.iter
  #
  #  Iterate over children.
  #  @param self object pointer.
  #  @return object.
  def iter(self):
    if self.is_object():
      for child in self.value:
        yield child
  ## PDSObject.iter_attribute
  #
  #  Iterate over current object attributes.
  #  @param self object pointer.
  #  @return object
  def iter_attribute(self):
    if self.is_object():
      for c in self.iter():
        if c.is_attribute():
          yield c

## PDSAttribute class documentation
#
#  Object used for representing PDSLabel attribute objects.
class PDSAttribute(PDSObject):
  ## PDSAttribute.__init__
  #
  #  PDSAttribute initialization.
  #  @param self object pointer.
  #  @param name object name.
  #  @param value attribute value.
  def __init__(self,name=None,value=None):
    ## Attribute name.
    self.name=name
    ## Attribute value.
    self.value=value
  ## PDSAttribute.summary
  #
  #  Print summary of the current object.
  #  @param self object pointer.
  def summary(self):
    print("attribute : ", self.name, self.value)
  ## PDSAttribute.valid
  #
  #  Check that the current object is valid.
  #  @param self object pointer.
  #  @return bool True is current object is valid, False otherwise.
  def valid(self):
    if self.name==PDS_END_TAG:
      return True
    return not self.name is None and not self.value is None
  ## PDSAttribute.is_equal
  #
  #  Check if current object is equal to another object.
  #  @param self object pointer.
  #  @param attr attribute object.
  #  @return bool True is both objects have the same name and same value.
  def is_equal(self,attr):
    return attr.name==self.name and attr.value==self.value
  ## PDSAttribute.__str__
  #
  #  PDSAttribute string representation.
  #  @param self object pointer.
  #  @param n_indent (int, default=0) number of indentation characters to insert at each line.
  #  @return str object string representation.
  def __str__(self,n_indent=0):
    return "{}PDSAttribute(name={},value={})".format(n_indent*"\t",self.name,self.value)
  ## PDSAttribute.fromstring
  #
  #  Create a PDSAttribute object from a string.
  #  @param in_str string we wish to parse.
  #  @return PDSAttribute object.
  @staticmethod
  def fromstring(in_str):
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
  ## PDSAttribute.next
  #
  #  Parse the next attribute object.
  #  @param in_str string we wish to parse.
  #  @return next attribute object if the string starts with an attribute definition. 
  @staticmethod
  def next(in_str):
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

## PDSLabel class documentation.
#
#  This class is used for storing PDS label information.
class PDSLabel:
  ## PDSLabel.__init__
  #
  #  PDSLabel object initialization.
  #  @param self object pointer.
  #  @param label_filename path to the label file.
  def __init__(self,label_filename):
    self.data=None
    self.parse(label_filename)
    self.column_index_map={}
    self.set_column_index_map()
  ## PDSLabel.set_column_index_map
  #
  #  Set the mapping between desired column names to the original column names.
  #  @param self object pointer.
  def set_column_index_map(self):
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
  ## PDSLabel.summary
  #
  #  Print a summary of the current object.
  #  @param self object pointer.
  def summary(self):
    print("PDS Label file")
    print("columns : ", self.column_count())
    for c in self.iter_column():
      print("\tcolumn : ",c.get("NAME"))
  ## PDSLabel.column_count
  #
  #  Count the number of columns defined in the label file.
  #  @param self object pointer.
  #  @return int number of column indexes.
  def column_count(self):
    count=0
    for c in self.iter_object("COLUMN"):
      count=count+1
    return count
  ## PDSLabel.iter_object
  #
  #  Iterate over children objects.
  #  @param self object pointer.
  #  @param t (default=None) only yield object of type <t>.
  #  @return yield objects.
  def iter_object(self, t=None):
    for o in self.data:
      if o.is_object():
        if t is None:
          yield o
        else:
          if o.is_type(t):
            yield o
        for so in o.iter_object(t):
          yield so
  ## PDSLabel.parse
  #
  #  Parse a PDS label file.
  #  @param self object pointer.
  #  @param filename path to the label file we want to parse.
  #  @return PDSLabel object.
  def parse(self, filename):
    s=readfile(filename)
    self.data=[]
    while len(s):
      obj, s=self.next(s) 
      if obj.valid():
        self.data.append(obj)
  ## PDSLabel.iter_column
  #
  #  Iterate over column type children.
  #  @param self object pointer.
  #  @return yield object.
  def iter_column(self):
    for c in self.iter_object("COLUMN"):
      yield c
  ## PDSLabel.next
  #
  #  Parse next PDS object from input.
  #  @param self object pointer.
  #  @param in_str string we wish to parse.
  #  @return next PDS object.
  def next(self,in_str):
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
  ## PDSLabel.find_column_by_name
  #
  #  Search for a column type child by name.
  #  @param self object pointer.
  #  @param col_name name of the columns.
  #  @return PDS column object.
  def find_column_by_name(self,col_name):
    for col in self.iter_column():
      if col.get("NAME")==col_name:
        return col

## PDSDataset class documentation
#
#  PDS dataset class.
class PDSDataset:
  ## PDSDataset.__init__
  #
  #  Dataset initialization.
  #  @param self object pointer.
  #  @param label_filename path to the PDS label file.
  #  @param data_filename path to the PDS data file.
  #  @param table_sep (default=",") PDS data file separation character.
  def __init__(self,label_filename="", data_filename="", table_sep=","):
    ## Path to the label file.
    self.label_filename=label_filename
    ## Path to the data file.
    self.data_filename=data_filename
    ## Data container.
    self.data=None
    self.load_data(data_filename,sep=table_sep)
    ## Label data.
    self.label_data=PDSLabel(label_filename=label_filename)
  ## PDSDataset.summary
  #
  #  Print a summary of the current object.
  #  @param self object pointer.
  def summary(self):
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
  ## PDSDataset.load_data
  #
  #  Load data from the data file.
  #  @param self object pointer.
  #  @param filename name of the file from which to load data.
  #  @param sep (default=",") separation character used in table.
  def load_data(self,filename,sep=","):
    # load data from csv type file, separation characters are spaces
    self.data=readfile(filename)
    self.data=np.array([list(filter(None,l.split(sep))) for l in self.data.split(NEWLINE) if len(l)], dtype=object)
  ## PDSDataset.shape
  #
  #  Get the current dataset shape.
  #  @param self object pointer.
  #  @return shape tuple.
  def shape(self):
    return len(self.data), len(self.data[0])
  ## PDSDataset.columns
  #
  #  Iterate over columns.
  #  @param self object pointer.
  #  @return yield object.
  def columns(self):
    # get columns index
    for col in self.label_data.iter_column():
      if not col is None:
        yield col
  ## PDSDataset.datetime_str_to_float
  #
  #  Convert a date represented as a string to a float.
  #  @param self object pointer.
  #  @param dt_str date string.
  #  @param scheme date formatting scheme.
  #  @return float, date utctimestamp.
  def datetime_str_to_float(self,dt_str,scheme=PDS_DATETIME_FORMAT):
    e=datetime.datetime.utcfromtimestamp(0)
    try:
      dt=datetime.datetime.strptime(dt_str,scheme)
    except:
      return None
    tts=(dt-e).total_seconds()
    return tts
  ## PDSDataset.column_data
  #
  #  Get column data.
  #  @param self object pointer.
  #  @param name column name.
  def column_data(self,col_name):
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
  ## PDSDataset.column_datatype
  #
  #  Get column datatype.
  #  @param self object pointer.
  #  @param col_name name of the target column.
  #  @return column datatype.
  def column_datatype(self,col_name):
    col=self.label_data.find_column_by_name(col_name)
    dt_str=col.get(PDS_FIELD_DATATYPE).replace("\"","")
    if dt_str==PDS_FLOAT:
      return np.float64
    if dt_str==PDS_INT:
      return np.intc    
    if dt_str==PDS_DATETIME:
      return "TIME"
    print("WARNING : datatype could not be found : " , dt_str)
  ## PDSDataset.column_index
  #
  #  Get column index.
  #  @param self object pointer.
  #  @param column name.
  #  @return int column index.
  def column_index(self,col_name):
    return self.label_data.column_index_map[col_name]
    for col in self.label_data.iter_column():
      if col.get("NAME")==col_name:
        items_att=col.get("ITEMS")
        if not items_att is None:
          first_index=int(col.get("COLUMN_NUMBER"))-1
          return [first_index+i for i in range(int(items_att))]
        return int(col.get("COLUMN_NUMBER"))-1
  ## PDSDataset.column_name_by_index
  #
  #  Search for column name by index.
  #  @param self object pointer.
  #  @param index index of the desired column.
  def column_name_by_index(self,index):
    for c in self.column_names():
      ind=self.column_index(c)
      if ind==index:
        return c
  ## PDSDataset.column_names
  #
  #  Iterate over column names.
  #  @param self object pointer.
  #  @return yield column name.
  def column_names(self):
    for c in self.columns():
      yield c.get(PDS_FIELD_NAME)
  ## PDSDataset.has_column
  #
  #  Check if the current object contains a column.
  #  @param self object pointer.
  #  @param col_name column name.
  #  @return True if dataset has column named <col_name> , False otherwise.
  def has_column(self, col_name):
    for c in self.column_names():
      if c == col_name:
        return True
    return False
  ## PDSDataset.time_column_name
  #
  #  Get the name of the column containing time data.
  #  @param self object pointer.
  #  @return column name , None if time wasn't found.
  def time_column_name(self):
    for c in self.column_names():
      if "time" in c.lower():
        return c
    return None
  ## PDSDataset.time_data
  #
  #  Get dataset time data.
  #  @param self object pointer.
  #  @return array of datetime ? np.array float?
  def time_data(self):
    time_col_name=self.time_column_name()
    if time_col_name is None:
      return np.array()
    return self.column_data(time_col_name)
  ## PDSDataset.timespan
  #
  #  Get the dataset timespan.
  #  @param self object pointer.
  #  @return start_time, stop_time tuple.
  def timespan(self):
    t=self.time_data()
    return t[0],t[-1]


