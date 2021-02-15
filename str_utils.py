## String manipulation functions.
#
#  @file str_utils.py
#  @author Alexandre Schulz
#  @brief functions for manipulation strings.

## str_is_integer
#
#  Check if string can be safely converted to integer.
#  @param in_str string to check.
#  @return bool.
def str_is_integer(in_str):
  numbers="01234567890"
  for k in in_str:
    if not k in numbers:
      return False
  return True
## str_join_list
#
#  Join elements of a list with a specified character.
#  @param lst list of elements.
#  @param c joining character.
#  @return string.
def str_join_list(lst, c=" "):
  a=""
  for e in lst:
    a=a+c+e
  return a
## str_rem_preceding
#
#  Remove all preceding occurences of a character in string.
#  @param in_str string input.
#  @param c (default=" ") default character.
#  @return string.
def str_rem_preceding(in_str,c=" "):
  a=in_str
  while a.startswith(c):
    a=a[len(c):]
  return a
## str_rem_trailing
#
#  Remove all trailing occurences of a character in string.
#  @param in_string string input.
#  @param c (default=" ") character to remove.
#  @return string.
def str_rem_trailing(in_str,c=" "):
  a=in_str
  while a.endswith(c):
    a=a[:-len(c)]
  return a
## str_rem_ends
#
#  Remove all preceding and trailing occurences of a character.
#  @param in_str input string.
#  @param c (default=" ") character to remove.
#  @return string.
def str_rem_ends(in_str,c=" "):
  a=in_str
  a=str_rem_preceding(a,c)
  a=str_rem_trailing(a,c)
  return a
## str_rem_successive
#
#  Replace successive occurences of given string in another string.
#  @param in_str input string.
#  @param c (default=" ") character we want to replace.
#  @return string.
def str_rem_successive(in_str,c=" "):
  a=in_str.split(c)
  a=list(filter(None,a))
  return str_join_list(a)
## readfile
#
#  Read a file and return content as string.
#  @param filename path to file.
#  @return string.
def readfile(filename):
  with open(filename,"r") as f:
    d=f.read()
    f.close()
    return d 


