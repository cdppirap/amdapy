"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:file: csv.py
:brief: simple CSV converter

"""

from amdapy.str_utils import readfile

class csv_dataset:
  """Simple CSV dataset container class
  """
  def __init__(self, data, columns=None):
    self.data=data
    self.columns=columns
class Parser:
  """I use this class for parsing CSV files to array objects
  """
  def __init__(self, ignore_line="#", sep="     "):
    self.ignore_line=ignore_line
    self.sep=sep
  def parse_string(self, in_str):
    a=csv_dataset([])
    n=None
    for line in in_str.split("\n"):
      # if line starts with the ignore_line character then skip it
      if line.startswith("# DATA_COLUMNS : "):
        a.columns=line.replace("# DATA_COLUMNS : ","").split(", ")
      if line.startswith(self.ignore_line):
        continue
      # otherwise split be sep character
      l_data=line.split(self.sep)
      # if answer is still empty
      if n is None:
        n=len(l_data)
        a.data.append(l_data)
      else:
        # otherwise check that the new line is the same size as the last one added to the solution
        if len(l_data)==n:
          a.data.append(l_data)
    return a
  def parse(self, filename):
    return self.parse_string(readfile(filename))

