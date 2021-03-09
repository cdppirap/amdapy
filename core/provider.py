"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Base classes for data providers

"""

class DataProvider:
  """Base class for providing access to dataset collections online

  :param name: name of the provider
  :type name: str
  """
  def __init__(self, name):
    """Object constructor
    """
    self.name=name
  def iter_dataset(self):
    """Iterate over dataset objects. This function does not do anything, it should be subclassed
    """
    return
    yield
