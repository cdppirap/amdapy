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
from amdapy.rest.client import get_obs_tree
from amdapy.core.parameter import Parameter
from amdapy.core.dataset import Dataset
from amdapy.core.collection import Collection

import matplotlib.pyplot as plt

class AMDA:
  """AMDA database connector. Use this object to connect to query AMDAs database. The :data:`collection`
  (:class:`Collection`) allows acces to dataset description. 

  .. code-block:: python

     >>> amda = amdapy.amda.AMDA()
     >>> for dataset in amda.collection.iter_dataset():
     >>>     print(dataset)

  """
  def __init__(self):
    """Object constructor
    """
    self.name="AMDA"
    self.collection=Collection()
  def _datasetel_to_dataset(self, datasetel, start, stop, sampling=None):
    """Convert a :class:`amdapy.rest.obstree.DatasetElement` object to a :class:`amdapy.amda.AMDADataset` object

    :param datasetel: dataset representation
    :type datasetel: amdapy.rest.obstree.DatasetElement
    :param start: data start time
    :type start: datetime.datetime
    :param stop: data stop time
    :type stop: datetime.datetime
    :param sampling: sampling in seconds
    :type sampling: float
    :return: dataset representation
    :rtype: amdapy.amda.AMDADataset

    """
    # get the data
    cols=self._get_column_names(datasetel)
    did=datasetel.id
    if stop is None:
      if start is None:
        start=datasetel.globalstart
        stop=start+datetime.timedelta(days=1)
      else:
        stop=start+datetime.timedelta(days=1)
    elif start is None:
      start=stop - datetime.timedelta(days=1)
    else:
      pass
    data=amdapy.rest.client.get_dataset(did, start, stop, cols, sampling=sampling)
    data.columns=cols
    data["Time"]=pd.to_datetime(data["Time"])
    data.set_index("Time",inplace=True)
    return Dataset(datasetel, data=data)

  def _get_column_names(self, datasetel):
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
  def get(self, item, start=None, stop=None, sampling=None):
    """Gets a item from the collection.

    :param item: collection item
    :type item: amdapy.amda._CollectionItem
    :param start: data start time
    :type start: datetime.datetime or str
    :param stop: data stop time 
    :type stop: datetime.datetime or str
    :param sampling: sampling in seconds
    :type sampling: float
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
    
    The :data:`start` and :data:`stop` attributes indicate the desired begining and end of the 
    data. If they are :class:`str` objects then they must follow the following scheme ::
      
      YYYY-MM-DDThh:mm:ss

    """
    # check that the dates provided are datetime objects, if not then convert them
    if isinstance(start, str):
      start=datetime.datetime.strptime(start,amdapy.rest.client.DATE_FORMAT) 
    if isinstance(stop , str):
      stop=datetime.datetime.strptime(stop, amdapy.rest.client.DATE_FORMAT)
    # check is item is a string, if it is then search for a dataset or parameter
    if isinstance(item, str):
      desc=self.collection.find(item)
      if desc is None:
        return None
      return self.get(desc,start, stop)
    if isinstance(item, Collection.Dataset):
      return self.get_dataset(item, start, stop, sampling=sampling)
    elif isinstance(item, Collection.Parameter):
      return self.get_parameter(item, start, stop, sampling=sampling)
    else:
      print("Error : argument item is not a Collection.Dataset or Collection.Parameter object")
      return None


























  def get_parameter(self, param, start=None, stop=None, sampling=None):
    """Get parameter data.

    :param param: parameter descriptor
    :type param: amda.Collection.Parameter 
    :param start: data start time
    :type start: datetime.datetime
    :param stop: data stop time
    :type stop: datetime.datetime
    :param sampling: sampling time in seconds
    :type sampling: float
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
    # check the display type
    if psize==1:
      col_names=[param.name]
    else:
      col_names=[param.name+"_"+str(k.name) for k in param.components]
    col_names=["Time"]+col_names
    if stop is None:
      if start is None:
        # get the parent dataset start and stop times
        parent_desc=self.collection.find(param.dataset_id)
        start=parent_desc.globalstart
        stop=start+datetime.timedelta(days=1)
      else:
        stop=start+datetime.timedelta(days=1)
    elif start is None:
      start=stop - datetime.timedelta(days=1)
    else:
      pass
    d=amdapy.rest.client.get_parameter(param.id, start,stop, col_names, sampling=sampling)
    d.set_index("Time", inplace=True)
    return Parameter(id=param.id, name=param.name, data=d,units=param.units)
  def get_dataset(self, dataset_item, start=None, stop=None, sampling=None):
    """Get dataset contents.

    :param dataset_item: dataset item
    :type dataset_id: Collection.Dataset
    :param start: data start time
    :type start: datetime.datetime
    :param stop: data stop time
    :type stop: datetime.datetime
    :param sampling: sampling in seconds
    :type sampling: float
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
    return self._datasetel_to_dataset(dataset_item, start, stop, sampling=sampling)


  def list_derived(self,userid, password):
      return amdapy.rest.client.list_derived(userid, password)
  def get_derived(self,userid, password, paramid, start, stop, sampling=None, col_names=None):
      return amdapy.rest.client.get_derived(userid,password,paramid,start,stop,sampling=sampling, col_names=col_names)
  


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


