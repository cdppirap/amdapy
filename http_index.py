## HTTP index utility functions.
#
#  @file http_index.py
#  @author Alexandre Schulz
#  @brief functions for accessing indexes and their subelements.
import os
import requests
from lxml import etree
from io import StringIO

PDS_INDEX_ROOT="https://pds-ppi.igpp.ucla.edu/data"
class HTTPIndex:
  ## HTTPIndex.__init__
  #
  #  HTTPIndex object initialization.
  def __init__(self, root):
    self.root=root
  def iter(self, root=None, tag=None):
    if root is None:
      for e in self.iter(root=self.root, tag=tag):
        yield e
    else:
      content=get_html_content(root)
      for el in content.iter(tag=tag):
        if isinstance(el,etree._Element) and (not isinstance(el,etree._Comment)):
          yield el
  ## HTTPIndex.iter_url
  #
  #  HTTPIndex iterator.
  #  @param self object pointer.
  def iter_url(self, root=None, recursive=False):
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
  def __init__(self, name, url=None):
    self.name=name
    self.url=url
    self.files=[]
    # iterate over all files under url
    self.index_manager=HTTPIndex(url)
  def load_files(self):
    for e in self.index_manager.iter_url(recursive=True):
      self.files.append(e)
  def __str__(self):
    a="PDSDataset(name:{},files:{})".format(self.name, len(self.files))
    for f in self.files:
      a="{}\n\t{}".format(a,f.split("/")[-1])
    return a


class PDSManager(HTTPIndex):
  def __init__(self):
    super(PDSManager,self).__init__(PDS_INDEX_ROOT)
  def iter_dataset(self):
    for l in self.iter(tag="a"):
      href=l.get("href")
      if valid_href(href):
        while href.endswith("/"):
          href=href[:-1]
        if len(href):
          yield PDSDataset(name=href, url=os.path.join(self.root,l.get("href")))
  def find(self, dataset_id):
    for dataset in self.iter_dataset():
      if dataset.name==dataset_id:
        return dataset
    return None

def valid_href(href):
  if href.startswith("http"):
    return False
  if href.startswith("?"):
    return False
  if href.startswith("/"):
    return False
  return True

def get_html_content(url):
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
