from apisvc import APIPool
from mvcsvc import MVCPool
from jobsvc import JOBPool
from procsvc import BusinessObjectPool
from caching import LRUCache, MemCached
import _ecfpyutils

_pool = {}

class CachePool(object):

  def __init__(self):
    self.cache_pool = {
        'USERS': LRUCache(32),
        'COMP': LRUCache(4),
        'DIVI' : LRUCache(8),
        'MISC': LRUCache(32),
        'LOCALE': LRUCache(64),
        'STATE': LRUCache(128),
      }
    if _ecfpyutils.memcached_isenabled():
      self.cache_pool['USERS'] = MemCached('USERS')
      self.cache_pool['COMP'] = MemCached('COMP')
      self.cache_pool['DIVI'] = MemCached('DIVI')
      self.cache_pool['STATE'] = MemCached('STATE')

  def getUserDict(self, user_name):
    usrdict = self.cache_pool['USERS']
    upusr = user_name.upper()
    return usrdict.get(upusr, None)

  def setUserDict(self, user_name, usr_dict):
    usrdict = self.cache_pool['USERS']
    upusr = user_name.upper()
    usrdict.put(upusr, usr_dict)

  def delUserDict(self, user_name):
    usrdict = self.cache_pool['USERS']
    upusr = user_name.upper()
    usrdict.put(upusr, None)

  def getCOMPDict(self, cono):
    codict = self.cache_pool['COMP']
    upcono = cono.upper()
    return codict.get(upcono, None)

  def setCOMPDict(self, cono, co_dict):
    codict = self.cache_pool['COMP']
    upcono = cono.upper()
    codict.put(upcono, co_dict)

  def delCOMPDict(self, cono):
    codict = self.cache_pool['COMP']
    upcono = cono.upper()
    codict.delete(upcono)

  def getDIVDict(self, cono, divi):
    dvdict = self.cache_pool['DIVI']
    upcono = cono.upper()
    updivi = divi.upper()
    return dvdict.get("%s-%s" % (upcono, updivi), None)

  def setDIVDict(self, cono, divi, dv_dict):
    dvdict = self.cache_pool['DIVI']
    upcono = cono.upper()
    updivi = divi.upper()
    dvdict.put("%s-%s" % (upcono, updivi), dv_dict)

  def delDIVDict(self, cono, divi):
    dvdict = self.cache_pool['DIVI']
    upcono = cono.upper()
    updivi = divi.upper()
    dvdict.delete("%s-%s" % (upcono, updivi))

  def getMISCDict(self, aname):
    msdict = self.cache_pool['MISC']
    upname = aname.upper()
    return msdict.get(upname, None)

  def setMISCDict(self, aname, ms_dict):
    msdict = self.cache_pool['MISC']
    upname = aname.upper()
    msdict.put(upname, ms_dict)

  def delMISCDict(self, aname):
    msdict = self.cache_pool['MISC']
    upname = aname.upper()
    msdict.delete(upname)

  def getLOCALEDict(self, aname):
    lodict = self.cache_pool['LOCALE']
    upname = aname.upper()
    return lodict.get(upname, None)

  def setLOCALEDict(self, aname, lo_dict):
    lodict = self.cache_pool['LOCALE']
    upname = aname.upper()
    lodict.put(upname, lo_dict)

  def delLOCALEDict(self, aname):
    lodict = self.cache_pool['LOCALE']
    upname = aname.upper()
    lodict.delete(upname)

  def getSTATEDict(self, usrname, pgm):
    statedict = self.cache_pool['STATE']
    the_key = "_".join((usrname, pgm))
    return statedict.get(the_key.upper(), None)

  def setSTATEDict(self, user_name, usr_dict):
    statedict = self.cache_pool['STATE']
    the_key = "_".join((usrname, pgm))
    statedict.put(upusr, statedict)

  def delSTATEDict(self, user_name):
    statedict = self.cache_pool['STATE']
    the_key = "_".join((usrname, pgm))
    statedict.put(the_key, None)

def getAPIPool():
  if not 'API' in _pool.keys():
    _pool['API'] = APIPool()
  return _pool['API']

def getMVCPool():
  if not 'MVC' in _pool.keys():
    _pool['MVC'] = MVCPool()
  return _pool['MVC']

def getJOBPool():
  if not 'JOB' in _pool.keys():
    _pool['JOB'] = JOBPool()
  return _pool['JOB']

def getOBJPool():
  if not 'BOBJ' in _pool.keys():
    _pool['BOBJ'] = BusinessObjectPool()
  return _pool['BOBJ']

def getCachePool():
  if not 'CACHE' in _pool.keys():
    _pool['CACHE'] = CachePool()
  return _pool['CACHE']

