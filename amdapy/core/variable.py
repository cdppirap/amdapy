"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: variable.py
:brief: Base classes and functions for manipulating variable objects.

Variables are the basic building block of a dataset, which is defined as a collection of variables.
In the context of the AMDA project the words "Variable" and "Parameter" are synonymous.
Variables are identified by their name, which should be unique within a dataset, and have the
following attributes : dtype, shape

We can set or acces the data through the bracket operator.

"""
import numpy as np

class Variable:
  """Base class for representing variable objects.

  :param name: name of the variable
  :type name: str
  :param dtype: variable datatype, optional
  :type dtype: numpy.dtype
  :param shape: shape of the variable, optional
  :type shape: tuple of ints
  :param value: variable data, optional
  :type value: numpy.array

  """
  def __init__(self, name, dtype=None, shape=None, value=None):
    """Object constructor
    """
    self.name=name
    self.shape=shape
    self.dtype=dtype
    self.value=value
    self.ndim=None
    if not self.value is None:
      self.shape=value.shape
      self.dtype=dtype
      self.ndim=len(self.shape)
  def __getitem__(self, i):
    """Data getter

    :param i: positon
    :type i: int
    :return: value of the item at desired position

    """
    return self.value[i]
  def __setitem__(self,key, value):
    """Data setter

    :param key: key at which to set item
    :type key: position
    :param value: value to set
    :type value: something

    """
    self.value[key]=value
  def __delitem__(self,key):
    """Data deletor

    :param key: positon
    :type key: position

    """
    pass
  def __eq__(self,other):
    """Check equality of two variables

    :param other: other Variable object we want to compare with
    :type other: amdapy.core.Variable

    """
    return self.name==other.name and \
           self.dtype==other.dtype and \
           self.shape==other.shape and \
           np.all(self.value== other.value)

  def __str__(self):
    """String representation of the object
    :return: string representation of the current object
    :rtype: str
    """
    return "Variable(name:{},dtype:{},shape:{})\n{}".format(self.name, self.dtype, self.shape, self.value)

if __name__=="__main__":
  print("Testing the Variable class definition")
  # create a variable object
  a=Variable("x",np.float64)
  print(a)
  # create a variable with some random data
  b=Variable("x",np.float64, data=np.random.random_sample(10))
  b[:3]=2
  print(b)
