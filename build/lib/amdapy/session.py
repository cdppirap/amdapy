"""AMDA session definition
:author: Alexandre Schulz
:file: session.py
"""
import sqlite3
import os
import numpy as np
import datetime

from amdapy.amdaWSClient.client import get_obs_tree, get_dataset
from amdapy.ddtime import dt_to_seconds

class Session:
  def __init__(self, dbpath="amda.db"):
    self.dbpath=dbpath
    self.datasets=[]
    self.conn=None
    self.init_database()
  def init_database(self):
    # check if the database exists
    if os.path.exists(self.dbpath):
      print("database exists")
    else:
      print("database does not exists")
    self.conn=sqlite3.connect(self.dbpath)
    # get list of table and update the dataset list
    for tname, in self.get_table_list():
        print(tname)
        nt=tname.replace("_","-")
        if not nt in self.datasets:
            self.datasets.append(nt)
  def get_table_list(self):
      l=[]
      for tname in self.conn.cursor().execute("select name from sqlite_master where type='table'").fetchall():
          l.append(tname)
      return l
  def add_dataset(self, dataset_id,start,stop):
    if self.contains_dataset(dataset_id):
      print("session contains dataset {}".format(dataset_id))
      t0,t1=self.get_table_timespan(dataset_id)
      t0=datetime.datetime.utcfromtimestamp(t0)
      t1=datetime.datetime.utcfromtimestamp(t1)
      print("check timespan : {} {}".format(t0,t1))
      if start < t0:
        print("start time is inferior then data start")
      if stop > t1:
        print("stop time is greater then data stop")
      return
    print("adding dataset to local session : {}".format(dataset_id))
    self.datasets.append(dataset_id)
    x=self.get_dataset_data(dataset_id,start,stop)
    print("done")
    # create a table to store the data
    cmd="CREATE TABLE {} (time real".format(dataset_id.replace("-","_"))
    for i in range(1,x.shape[1]):
      cmd="{},{}".format(cmd,"val{} {}".format(i,"real"))
    cmd="{})".format(cmd)
    
    c=self.conn.cursor()
    c.execute(cmd)
    self.conn.commit()
    for i in range(x.shape[0]):
      # parse date
      dt=datetime.datetime.strptime(x.iloc[i,0],"%Y-%m-%dT%H:%M:%S.%f")
      tuc=dt_to_seconds(dt)
      cmd="INSERT INTO {} VALUES ({}".format(dataset_id.replace("-","_"),tuc)
      for j in range(1,x.shape[1]):
          cmd="{}, {}".format(cmd,x.iloc[i,j])
      cmd="{})".format(cmd)
      self.conn.execute(cmd)
      self.conn.commit()
  def get_table_timespan(self,dataset_id):
    max_t=self.conn.cursor().execute("select MAX(Time) from {}".format(dataset_id.replace("-","_"))).fetchone()
    min_t=self.conn.cursor().execute("select MIN(Time) from {}".format(dataset_id.replace("-","_"))).fetchone()
    return min_t[0],max_t[0]
  def contains_dataset(self,dataset_id):
    # get list of table
    a=self.conn.cursor().execute("SELECT * FROM sqlite_master WHERE type='table'")
    for ttype,tname,twhat,tsize,_ in a.fetchall():
        print("puh",tname,dataset_id.replace("-","_"))
        if tname==dataset_id.replace("-","_"):
            return True
    return dataset_id in self.datasets
  def get_dataset_data(self, dataset_id,start,stop):
    # get the AMDA tree
    amda_tree=get_obs_tree()
    # get the dataset element
    dataset_el=amda_tree.find_dataset(dataset_id)
    if dataset_el is None:
      print("Error : could not find dataset {}".format(dataset_id))
      return
    # get the dataset
    return get_dataset(dataset_el.id, start,stop)
  def get_dataset(self, dataset_id):
    if self.contains_dataset(dataset_id):
      a=self.conn.cursor().execute("select * from {}".format(dataset_id.replace("-","_")))
      l=[]
      for el in a.fetchall():
        l.append(el)
      return np.array(l,dtype=object)
    if not dataset_id in self.datasets:
      print("Session does not contain dataset {}".format(dataset_id))
      return
    return self.datasets[dataset_id]

