__author__ = "Jaimy Azle"
__version__ = '0.0.1'

import _dbxapi
import types
import string
import time
import datetime

### module constants

# compliant with DB SIG 2.0
apilevel = '2.0'

# module may be shared, but not connections
threadsafety = 1

# this module use extended python format codes
paramstyle = 'pyformat'

#export column type names from _dbxapi
class DBAPITypeObject:
  def __init__(self,*values):
    self.values = values
  def __cmp__(self,other):
    if other in self.values:
      return 0
    if other < self.values:
      return 1
    else:
      return -1

STRING = DBAPITypeObject(1)
BINARY = DBAPITypeObject(2)
NUMBER = DBAPITypeObject(3)
DATETIME = DBAPITypeObject(4)
DECIMAL = DBAPITypeObject(5)

class Warning(StandardError):
  pass

class Error(StandardError):
  pass

class InterfaceError(Error):
  pass

class DatabaseError(Error):
  pass

class DataError(DatabaseError):
  pass

class OperationalError(DatabaseError):
  pass

class IntegrityError(DatabaseError):
  pass

class InternalError(DatabaseError):
  pass

class ProgrammingError(DatabaseError):
  pass

class NotSupportedError(DatabaseError):
  pass


### cursor object

class pydbxCursor:

  def __init__(self, src):
    self.__source = src
    self.description = None
    self.rowcount = -1
    self.arraysize = 1
    self._result = []
    self.__fetchpos = 0
    self.__resultpos = 0

  def close(self):
    self.__source = None
    self.description = None
    self.result = []
    self.rowcount = -1

  def execute(self, operation, params = None):
    # "The parameters may also be specified as list of
    # tuples to e.g. insert multiple rows in a single
    # operation, but this kind of usage is depreciated:
    if params and type(params) == types.ListType and \
          type(params[0]) == types.TupleType:
      self.executemany(operation, params)
    else:
      # not a list of tuples
      self.executemany(operation, (params,))

  def executemany(self, operation, param_seq):
    self.description = None
    self.rowcount = -1
    self.__fetchpos = 0
    self.__resultpos = 0

    # first try to execute all queries
    totrows = 0
    sql = ""
    try:
      for params in param_seq:
        if params != None:
          sql = _quoteparams(operation, params)
        else:
          sql = operation
        # print sql
        ret = self.__source.query(sql)
        if ret == 1:
          self._result = self.__source.fetch_array()
          totrows = totrows + self._result[self.__resultpos][1]
        else:
            self._result = None
            raise DatabaseError, "error: could not fetch result"
    except:
      raise

    # then initialize result raw count and description
    if len(self._result[self.__resultpos][0]) > 0:
      self.description = map(lambda (colname,coltype): (colname, coltype, None, None, None, None, None),self._result[self.__resultpos][0])
      self.rowcount = totrows
    else:
      self.description = None
      self.rowcount = self._result[self.__resultpos][1]

  def nextset(self):
    if self._result ==None:
      return 0

    resultlen =len(self._result)
    if resultlen>1 and self.__resultpos+1<resultlen:
      self.__resultpos = self.__resultpos + 1
      return 1
    else:
      return 0

  def fetchone(self):
    ret = self.fetchmany(1)
    if ret: return ret[0]
    else: return None

  def fetchall(self):
    return self._result[self.__resultpos][2][self.__fetchpos:]

  def fetchmany(self, size = None, keep = 1):
    if size == None:
      size = self.arraysize
    if keep == 1:
      self.arraysize = size
    res = self._result
    if res[self.__resultpos][1]==self.__fetchpos:
        return []
    reslen = len(res[self.__resultpos][2][self.__fetchpos:])
    if reslen < size:
        size = res[self.__resultpos][1]
    ret = res[self.__resultpos][2][self.__fetchpos:self.__fetchpos+size]
    self.__fetchpos = self.__fetchpos + size
    return ret

  def setinputsizes(self, sizes):
    pass

  def setoutputsize(self, size, col = 0):
    pass

def _quote(x):
  if type(x) == types.StringType:
    x = "'" + string.replace(str(x), "'", "''") + "'"
  elif type(x) in (types.IntType, types.LongType, types.FloatType):
    pass
  elif x is None:
    x = 'NULL'
  # datetime quoting
  # described under "Writing International Transact-SQL Statements" in BOL
  # beware the order: isinstance(x,datetime.date)=True if x is
  # datetime.datetime ! Also round x.microsecond to milliseconds,
  # otherwise we get Msg 241, Level 16, State 1: Syntax error
  elif isinstance(x, datetime.datetime):
    x = "{ts '%04d-%02d-%02d %02d:%02d:%02d.%s'}" % \
      (x.year,x.month, x.day,
      x.hour, x.minute, x.second, x.microsecond / 1000)
  elif isinstance(x, datetime.date):
    x = "{d '%04d-%02d-%02d'}" % (x.year, x.month, x.day)
  # alternative quoting by Luciano Pacheco <lucmult@gmail.com>
  #elif hasattr(x, 'timetuple'):
  # x = time.strftime('\'%Y%m%d %H:%M:%S\'', x.timetuple())
  else:
    #print "didn't like " + x + " " + str(type(x))
    raise InterfaceError, 'do not know how to handle type %s' % type(x)

  return x

def _quoteparams(s, params):
  if hasattr(params, 'has_key'):
    x = {}
    for k, v in params.items():
      x[k] = _quote(v)
    params = x
  else:
    params = tuple(map(_quote, params))
  return s % params



### connection object

class pydbxCnx:

  def __init__(self, cnx):
    self.__cnx = cnx
    try:
      self.__cnx.query("begin tran")
      self.__cnx.fetch_array()
    except:
      raise OperationalError, "invalid connection."
    # self.__cnx = cnx
    # try:
    #  transid = self.__cnx.beginTrans()
    #  self.__cnx.commit(transid)
    #except:
    #  raise OperationalError, "invalid connection."

  def close(self):
    if self.__cnx == None:
      raise OperationalError, "invalid connection."
    self.__cnx.close()
    self.__cnx = None

  def commit(self):
    if self.__cnx == None:
      raise OperationalError, "invalid connection."
    try:
      self.__cnx.query("commit tran")
      self.__cnx.fetch_array()
      self.__cnx.query("begin tran")
      self.__cnx.fetch_array()
    except:
      raise OperationalError, "can't commit."
    # if self.__cnx == None:
    #   raise OperationalError, "invalid connection."
    # try:
    #  if self.transid:
    #     self.__cnx.commit(self.transid)
    #   self.transid = self.__cnx.beginTrans()
    # except:
    #   raise OperationalError, "can't commit."

  def rollback(self):
    if self.__cnx == None:
      raise OperationalError, "invalid connection."
    try:
      self.__cnx.query("rollback tran")
      self.__cnx.fetch_array()
      self.__cnx.query("begin tran")
      self.__cnx.fetch_array()
    except:
      raise OperationalError, "can't rollback."
    # if self.__cnx == None:
    #   raise OperationalError, "invalid connection."
    # try:
    #   if self.transid:
    #     self.__cnx.rollback(self.transid)
    #   self.transid = self.__cnx.beginTrans()
    # except:
    #   raise OperationalError, "can't rollback."

  def cursor(self):
    if self.__cnx == None:
      raise OperationalError, "invalid connection."
    try:
      return pydbxCursor(self.__cnx)
    except:
      raise OperationalError, "invalid connection."

# connects to a database
def connect(dsn = None, drv="", getdrvfnc="", libnm="", vlibnm=""):
  # open the connection
  dbdsn = dsn.strip()
  if dbdsn != '':
    dbdict = dict([x.split('=') for x in dsn.split(';')])
    dbdrv = dbdict.pop('DriverName') if dbdict.has_key('DriverName') else drv
    dbgetdrvfnc = dbdict.pop('GetDriverFunc') if dbdict.has_key('GetDriverFunc') else getdrvfnc
    dblibnm = dbdict.pop('LibraryName') if dbdict.has_key('LibraryName') else libnm
    dbvlibnm = dbdict.pop('VendorLibName') if dbdict.has_key('VendorLibName') else vlibnm
    dbdsn = '\n'.join(['%s=%s' % (key, value) for key, value in dbdict.iteritems()])
  else:
    dbdrv = drv
    dbgetdrvfnc = getdrvfnc
    dblibnm = libnm
    dbvlibnm = vlibnm
  con = _dbxapi.getdbxconn(dbdrv, dbgetdrvfnc, dblibnm, dbvlibnm, dbdsn)
  return pydbxCnx(con)


