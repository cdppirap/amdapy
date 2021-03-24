import datetime

class Timespan:
  """Time interval container class

  :param start: start date time
  :type start: datetime.datetime or None
  :param stop: stop date time
  :type stop: datetime.datetime
  """
  def __init__(self, start, stop):
    """Object constructor
    """
    self.start=start
    self.stop=stop
  def __contains__(self, o):
    """Check if timespan contains another object

    :param o: object to check, can be a datetime object or a Timespan
    :type o: datetime.datetime or Timespan
    :return: True if current timespan object contains :data:`o`
    :rtype: True or False
    """
    if isinstance(o, datetime.datetime):
      return self.start <= o and self.stop > o
    if isinstance(o, Timespan):
      return self.start <= o.start and self.stop > o.stop
    return False


