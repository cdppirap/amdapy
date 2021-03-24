import sys
sys.path.insert(0,"/home/aschulz/amdapy")
import amdapy
from amdapy.amda import AMDA
import datetime

def try_getting_data(data_desc, amda_conn, string_1, err_string, start, stop):
  print(string_1)
  try:
    data=amda_conn.get(data_desc, start, stop)
  except Exception as e:
    print("{} : {}".format(err_string, e))
def try_getting_first_hour_of_data(parameter_description, dataset_description, amda_conn):
  t_int=[dataset_description.starttime, 0]
  t_int[-1]=t_int[0]+datetime.timedelta(hours=1)
  try_getting_data(dataset_description, amda, "Trying to get first hour of full dataset...", \
          "\tError", t_int[0], t_int[1])
  try_getting_data(parameter_description, amda_conn, "Trying to get first hour of parameter...", \
          "\tError", t_int[0], t_int[1])
def try_getting_full_data(parameter_description, dataset_description, amda_conn):
  t_int=[dataset_description.starttime, dataset_description.stoptime]
  try_getting_data(dataset_description, amda, "Trying to get full dataset...", \
          "\tError", t_int[0], t_int[1])
  try_getting_data(parameter_description, amda_conn, "Trying to get full parameter...", \
          "\tError", t_int[0], t_int[1])
def try_getting_1_month_data(parameter_description, dataset_description, amda_conn):
  t_int=[dataset_description.starttime, dataset_description.starttime+datetime.timedelta(days=30)]
  try_getting_data(dataset_description, amda, "Trying to getting first month dataset...", \
          "\tError", t_int[0], t_int[1])
  try_getting_data(parameter_description, amda_conn, "Trying to get first month parameter...", \
          "\tError", t_int[0], t_int[1])
def try_getting_last_month_data(parameter_description, dataset_description, amda_conn):
  t_int=[dataset_description.stoptime-datetime.timedelta(days=30), dataset_description.stoptime]
  try_getting_data(dataset_description, amda, "Trying to getting last month dataset...", \
          "\tError", t_int[0], t_int[1])
  try_getting_data(parameter_description, amda_conn, "Trying to get last month parameter...", \
          "\tError", t_int[0], t_int[1])





amda=AMDA()
param_d=amda.collection.find("al")
dataset_d=amda.collection.find(param_d.dataset_id)
## Try to get the first hour of data
try_getting_first_hour_of_data(param_d, dataset_d, amda)
try_getting_full_data(param_d, dataset_d, amda)
try_getting_1_month_data(param_d, dataset_d, amda)
try_getting_last_month_data(param_d, dataset_d, amda)
