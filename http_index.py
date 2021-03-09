"""
:author: Alexandre Schulz
:file: http_index.py
:brief: Classes and functions for navigating HTML basic indexes and retriving the files
        linked within.

Data providers often provide access to their data via a multitude of means. A simple one to 
interact with are HTML indexes of the dataset file hiarchy. The classes and functions defined
in this file aim to provide easy access to the elements of the index.

The class provides iterators for going over the files listed in the index either recursively 
or not.

NOTE : this class is not well named.
"""
import os
import requests
from lxml import etree
from io import StringIO

PDS_INDEX_ROOT="https://pds-ppi.igpp.ucla.edu/data"
class HTTPIndex:
  """HTTPIndex
  :brief: Base class for reading an HTMLIndex.
  
  This is the base class that we use for accessing elements contained in an index. The index
  is just a table containing links. Those links either point to a file that we can download
  (leaf of the tree) or a folder. The HTTPIndex class provides iterators for navigating the
  elements of the index and retrieving the addresses of resources we are interested in.

  In most cases we will have to subclass this class to adapt its behaviour to the specific index
  we are working with.

  """
  def __init__(self, root):
    """HTTPIndex initialization
    :param self: object pointer
    :param root: index root URL
    :type root: string
    :brief: Initialize the index manager object.
    """
    self.root=root
  def iter(self, root=None, tag=None):
    """HTTPIndex URL iterator : iterate over elements of the tree. Yields lxml.etree._Element objects.
    :param root: root URL of the index (default is None, the default PDS index will be used.
    :type root: str or None
    :param tag: only yield specific tags
    :type tag: str or None
    :return: lxml.etree._Element object
    """
    if root is None:
      for e in self.iter(root=self.root, tag=tag):
        yield e
    else:
      content=get_html_content(root)
      for el in content.iter(tag=tag):
        if isinstance(el,etree._Element) and (not isinstance(el,etree._Comment)):
          yield el
  def iter_url(self, root=None, recursive=False):
    """HTTPIndex iter_url : yield URL objects contained in the index.
    :param root: root URL of the index or None.
    :type root: str or None
    :param recursive: traverse tree resursively
    :type recursive: True or False
    """
    if root is None:
      for l in self.iter_url(root=self.root,recursive=recursive):
        yield l
    else:
      for el in self.iter(root=root, tag="a"):
        href=el.get("href")
        if not valid_href(href):
          continue
        else:
          n_url=os.path.join(root, href)
          if href.endswith("/"):
            if not recursive:
              yield n_url
            else:
              for e in self.iter_url(n_url):
                yield e
          else:
            yield n_url
              
class PDSDataset:
  """This class provides access to datasets stored in the PDS ASCII format.
  
  :param name: name of the dataset
  :type name: str
  :param url: URL of the resource file
  :type url: str
  """
  def __init__(self, name, url=None):
    """Object initialization
    """
    self.name=name
    self.url=url
    self.files=[]
    # iterate over all files under url
    self.index_manager=HTTPIndex(url)
  def load_files(self):
    """Load all files associated with the dataset name we have chosen.
    """
    for e in self.index_manager.iter_url(recursive=True):
      self.files.append(e)
  def __str__(self):
    """PDSDataset string representation

    :return: current object string representation
    :rtype: str
    """
    a="PDSDataset(name:{},files:{})".format(self.name, len(self.files))
    for f in self.files:
      a="{}\n\t{}".format(a,f.split("/")[-1])
    return a


class PDSManager(HTTPIndex):
  """Base class for managing data provided by the PDS data provider.
  """
  def __init__(self):
    """Object constructor
    """
    super(PDSManager,self).__init__(PDS_INDEX_ROOT)
  def iter_dataset(self):
    """Iterate over dataset objects

    :return: dataset objects
    :rtype: amdapy.http_index.PDSDataset
    """
    for l in self.iter(tag="a"):
      href=l.get("href")
      if valid_href(href):
        while href.endswith("/"):
          href=href[:-1]
        if len(href):
          yield PDSDataset(name=href, url=os.path.join(self.root,l.get("href")))
  def find(self, dataset_id):
    """Find a dataset by name

    :param dataset_id: identification of the dataset
    :type dataset_id: str
    :return: PDS dataset object if the :data:`dataset_id` corresponds to a dataset, None otherwise
    :rtype: amdapy.http_index.PDSDataset or None
    """
    for dataset in self.iter_dataset():
      if dataset.name==dataset_id:
        return dataset
    return None

def valid_href(href):
  """Check if a link is valid

  :param href: value of the link
  :type href: str
  :return: True if link is valid, false otherwise
  :rtype: bool
  """
  if href.startswith("http"):
    return False
  if href.startswith("?"):
    return False
  if href.startswith("/"):
    return False
  return True

def get_html_content(url):
  """Get HTML content from URL into str object

  :param url: URL address
  :type url: str
  :return: content of the URL address
  :rtype: str
  """
  a=requests.get(url)
  t=etree.parse(StringIO(a.text), etree.HTMLParser())
  return t

if __name__=="__main__":
  print("HTTPIndex test")
  # create an index object
  pds_manager=PDSManager()
  dataset_id="M10-H-MAG-3-RDR-M1-HIGHRES-V1.0"
  dataset=pds_manager.find(dataset_id)
  if not dataset is None:
    print("loading dataset files")
    dataset.load_files()
    print(dataset)
