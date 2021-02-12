## DDIime manipulation functions.
#
#  @file ddtime.py
#  @author Alexandre Schulz
#  @brief Functions and classes for manipulating time represented in the DDTime format.
import datetime

class DDTime:
  @staticmethod
  def from_utctimestamp(t):
    return DDTime.from_datetime(datetime.datetime.utcfromtimestamp(t))
  @staticmethod
  def from_datetime(dt):
    return ddtime2(dt)
## dt_to_doy
#
#  Convert datetime object to DayOfYear
#  @param dt datetime object.
#  @return int
def dt_to_doy(dt):
  return int(dt.strftime("%j"))
## ddtime
#
#  Get DDTime for datetime.
#  @param dt datetime object.
#  @return DDTime.
def ddtime2(dt):
  doy=dt_to_doy(dt)
  print("{:04d} {:03d} {:02d} {:02d} {:02d} {}".format(dt.year, doy-1, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))[:16])
  return "{:04d}{:03d}{:02d}{:02d}{:02d}{:03d}".format(dt.year, doy-1, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))[:16]+"\0"

