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
  """Base class for representing Variable
  """
  def __init__(self, name, dtype=None, shape=None, data=None):
    """Variable initialization
    :param name: name of the variable.
    :type name: string
    :param dtype: dtype of the variable
    :type dtype: numpy dtype
    :param shape: shape of the variable
    :type shape: tuple of ints
    """
    self.name=name
    self.shape=shape
    self.dtype=dtype
    self.data=data
    if not self.data is None:
      self.shape=data.shape
      self.dtype=dtype
  def __getitem__(self, i):
    """Data getter
    :param i: positon
    :type i: int
    :return: value of the item at desired position
    """
    return self.data[i]
  def __setitem__(self,key, value):
    """Data setter
    :param key: key at which to set item
    :type key: position
    :param value: value to set
    :type value: something
    """
    self.data[key]=value
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
           np.all(self.data == other.data)

  def __str__(self):
    """String representation of the object
    """
    return "Variable(name:{},dtype:{},shape:{})\n{}".format(self.name, self.dtype, self.shape, self.data)

if __name__=="__main__":
  print("Testing the Variable class definition")
  # create a variable object
  a=Variable("x",np.float64)
  print(a)
  # create a variable with some random data
  b=Variable("x",np.float64, data=np.random.random_sample(10))
  b[:3]=2
  print(b)
