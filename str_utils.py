"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Commonly used functions that deal with manipulation string objects

Collection of simple functions for manipulating strings such as reading file, splitting , blablabla

"""

def str_is_integer(in_str):
  """Check if string can safely be converted to integer

  :param in_str: string we want to check
  :type in_str: str
  :return: True if the string represents an integer, False otherwise
  :rtype: bool
  """
  numbers="01234567890"
  for k in in_str:
    if not k in numbers:
      return False
  return True
def str_join_list(lst, c=" "):
  """Join a list of strings with a separation character

  :param lst: list of strings we want to join
  :type lst: list of str objects
  :param c: separation character, optional , default is space
  :type c: str
  :return: string obtained by joining all elements of lst
  :rtype: str
  """
  a=""
  for e in lst:
    a=a+c+e
  return a
def str_rem_preceding(in_str,c=" "):
  """Remove all preceding occurences of a string in another string.

  :param in_str: string from which we want to remove all preceding occurences of :data:`c`
  :type in_str: str
  :param c: pattern we want to remove , optional, default removes spaces.
  :type c: str
  :return: str obtained by removing all preceding occurences of :data:`c` in :data:`in_str`
  :rtype: str
  """
  a=in_str
  while a.startswith(c):
    a=a[len(c):]
  return a
def str_rem_trailing(in_str,c=" "):
  """Remove all trailing occurences of a string in another string.

  :param in_str: string from which we want to remove all trailing occurences of :data:`c`
  :type in_str: str
  :param c: pattern we want to remove , optional, default removes spaces.
  :type c: str
  :return: str obtained by removing all trailing occurences of :data:`c` in :data:`in_str`
  :rtype: str
  """
  a=in_str
  while a.endswith(c):
    a=a[:-len(c)]
  return a
def str_rem_ends(in_str,c=" "):
  """Combination of the previous two functions, removes all preceding and trailing occurences of :data:`c` in :data:`in_str`

  :param in_str: string from which we want to remove all preceding and trailing occurences of :data:`c`
  :type in_str: str
  :param c: pattern we wish to remove, optional, default removes spaces
  :type c: str
  :return: string obtained by removing all preceding and trailing occurences of :data:`c` in the input
  :rtype: str
  """
  a=in_str
  a=str_rem_preceding(a,c)
  a=str_rem_trailing(a,c)
  return a
def str_rem_successive(in_str,c=" "):
  """Remove successive occurences of a pattern in the input string and replace by a single occurence

  :param in_str: input string
  :type in_str: str
  :param c: pattern to remove, optional, default replaces spaces
  :type c: str
  :return: string obtained by replacing successive occurences of :data:`c` in the input by a single occurence
  :rtype: str
  """
  a=in_str.split(c)
  a=list(filter(None,a))
  return str_join_list(a)
def readfile(filename):
  """Read file and return content as str object

  :param filename: path to the file we wish to read
  :type filename: str
  :return: content of the file in a str object
  :rtype: str
  """
  with open(filename,"r") as f:
    d=f.read()
    f.close()
    return d 


