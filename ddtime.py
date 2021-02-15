## DDIime manipulation functions.
#
#  @file ddtime.py
#  @author Alexandre Schulz
#  @brief Functions and classes for manipulating time represented in the DDTime format.
import datetime

class DDTime:
  """DDTime class. AMDA specific time representation and methods for parsing from string and generating from datetime objects.
  :class: amdapy.ddtime
  """
  @staticmethod
  def from_utctimestamp(t):
    """Convert UTC timestamp to DDTime.

    :param t: UTC timestamp.
    :type t: float
    :return: DDTime
    :rtype: str
    """
    return DDTime.from_datetime(datetime.datetime.utcfromtimestamp(t))
  @staticmethod
  def from_datetime(dt):
    """Convert datetime to DDTime.

    :param dt: datetime object.
    :type dt: datetime.datetime
    :return: DDTime
    :rtype: str
    """
    return ddtime2(dt)
## dt_to_doy
#
#  Convert datetime object to DayOfYear
#  @param dt datetime object.
#  @return int
def dt_to_doy(dt):
  """Get DOY from datetime object.

  :param dt: datetime object.
  :type dt: datetime.datetime
  :return: day of year.
  :rtype: int
  """
  return int(dt.strftime("%j"))
## ddtime
#
#  Get DDTime for datetime.
#  @param dt datetime object.
#  @return DDTime.
def ddtime2(dt):
  """Temporary.
  
  :param dt: datetime.
  :type dt: datetime.datetime
  :return: DDTime
  :rtype: str
  """
  doy=dt_to_doy(dt)
  return "{:04d}{:03d}{:02d}{:02d}{:02d}{:03d}".format(dt.year, doy-1, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))[:16]+"\0"

