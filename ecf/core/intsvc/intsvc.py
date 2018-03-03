import sys
import copy
import string
import ecfexceptions
from procsvc import getBOProxy

_moduleClassList = {}
_classPool = {}
_services = {}
_groups = {}

class INTService(object):

  def __init__(self, name):
    _services[name] = self
    self._name = name
    self._methods = {}
    self._exportedMethods = None

  def joinGroup(self, name):
    if not name in _groups:
      _groups[name] = {}
    _groups[name][self._name] = self

  def exportMethod(self, proc):
    if callable(proc):
      self._methods[proc.__name__] = proc

  def abortResponse(self, description, origin, details):
    raise ecfexceptions.ECFINTServiceNotAvailable("%s -- %s: %s"%(origin,description,details))

  def getBusinessObjectProxy(self):
    return getBOProxy()

class INTLocalService(INTService):

  def __init__(self, name):
    self._name = name

  def initsvc(self):
    if not _services.has_key(self._name):
      raise Exception('Key %s is not found' % (self._name, ))
    svc = _services[self._name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

def createINTLocalService(name):
  localsvc = INTLocalService(name)
  localsvc.initsvc()
  return localsvc

def getINTLocalService(name):
  return createINTLocalService(name)