#
# Copyright (c) 2009 Cipta Solusi Pratama. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Cipta Solusi Pratama'

import sys
import ecfexceptions
import datetime as dt
from procsvcutil import BusinessObjectClassMutator, process_mutators
from jitutil import *

_moduleClassList = {}
_classPool = {}
_services = {}
_groups = {}

__all__= ('BusinessObject', 'BusinessObjectPool',
          'BusinessObjectService', 'BusinessObjectLocalService',
          'getBOProxy')

bobjs = list()

options_defaults = dict(
  inheritance='single',
  polymorphic=False,
  bobjname=None,
  allowcoloverride=False
  )

class BusinessObjectService(object):
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
    raise ecfexceptions.ECFBOServiceNotAvailable("%s -- %s: %s"%(origin,description,details))

class BusinessObjectLocalService(BusinessObjectService):

  def __init__(self, name):
    self._name = name
    svc = _services[name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

class BusinessObjectPool(BusinessObjectService):

  def __init__(self):
    self._objPool = {}
    super(BusinessObjectPool, self).__init__('__BOBJPROXY__')
    self.joinGroup('__BOBJSVC__')
    self.exportMethod(self.getObject)

  def getObject(self, obj):
    ob = self._objPool.get(obj)
    if not ob:
      self.abortResponse('Object Error', 'warning',
        'Business Object %s does not exist' % str(obj))
    else:
      if not getattr(ob, '_active', True):
        self.abortResponse('Object Error', 'warning',
        'Business Object %s is not active' % str(obj))
      else:
        return ob.instantiate()
    return None

  def add(self, name, objInstance):
    if self._objPool.has_key(name):
      del self._objPool[name]
    self._objPool[name] = objInstance

  def get(self, name):
    return self._objPool.get(name, None)

  def instanciate(self, module):
    return [klass.createInstance(self, module) \
              for klass in _moduleClassList.get(module, [])]


class BusinessObjectDescriptor(object):
  def __init__(self, bobj, name):
    self.bobj = bobj
    module = str(bobj)[6:]
    module = module[:len(module)-1]
    module = module.split('.')[1][:6]
    self.module = module
    self.fields = []
    self.parent = None
    self.children = []
    for base in bobj.__bases__:
      if issubclass(base, BusinessObject) and base is not BusinessObject:
        if self.parent:
          raise Exception('%s business object inherits from several objects,'
            ' and this is not supported.'
            % self.bobj.__name__)
        else:
          self.parent = base
          self.parent._descriptor.children.append(bobj)
    self.properties = dict()
    for option in options_defaults.keys():
      setattr(self, option, options_defaults[option])

    self.collection = getattr(self.module, '__bobj_collection__',
                                  bobjs)
    _moduleClassList.setdefault(self.module, []).append(bobj)
    _classPool[name] = bobj

  def add_property(self, name, property, check_duplicate=True):
    if check_duplicate and name in self.properties:
        raise Exception("property '%s' already exist in '%s' ! " %
                        (name, self.bobj.__name__))
    self.properties[name] = property

  def get_field(self, fieldname):
    for field in self.fields:
      if field.properties.name == fieldname:
        return field
    return None

  def setup_options(self):
    '''
    Setup any values that might depend on using_options. For example, the
    obj.name.
    '''
    if self.collection is not None:
      self.collection.append(self.bobj)

    bobj = self.bobj
    if self.inheritance == 'concrete' and self.polymorphic:
      raise NotImplementedError("Polymorphic concrete inheritance is "
                                  "not yet implemented.")

    if self.parent:
      if self.inheritance == 'single':
        self.bobjname = self.parent._descriptor.bobjname
    if not self.bobjname:
      self.bobjname = bobj.__name__.upper()
    elif callable(self.bobjname):
      self.bobjname = self.bobjname (bobj)


def _is_bobj(class_):
  return isinstance(class_, BusinessObjectMeta)

class BusinessObjectMeta(type):

  _bobjs = {}

  def __init__(cls, name, bases, dict):
    if bases[0] is object:
      return

    # build a dict of entities for each frame where there are entities
    # defined
    caller_frame = sys._getframe(1)
    cid = cls._caller = id(caller_frame)
    caller_bobjs = BusinessObjectMeta._bobjs.setdefault(cid, {})
    caller_bobjs[name] = cls

    # Append all bobjs which are currently visible by the mvc. This
    # will find more entities only if some of them where imported from
    # another module.
    for bobj in [e for e in caller_frame.f_locals.values()
                     if _is_bobj(e)]:
        caller_bobjs[bobj.__name__] = bobj

    desc = cls._descriptor = BusinessObjectDescriptor(cls, name)

    # process mutators
    process_mutators(cls)

    # setup misc options here (like bobjname etc.)
    desc.setup_options()

  def __call__(cls, *args, **kwargs):
    return type.__call__(cls, *args, **kwargs)


class BusinessObject(object):
  """
  Base class of business object list
  """

  __metaclass__ = BusinessObjectMeta

  def __init__(self, pool):
    if pool is not None:
      pool.add(self._descriptor.bobjname, self)
      self.pool = pool
    else:
      self.pool = None

  @nativemethod
  def setAuditFields(self, obj, user):
    auditfields = ('AUDT', 'AUTM', 'AUUS')
    now = dt.datetime.now()
    aufield = [prop.name for prop in obj.__class__._descriptor.builders \
      if prop.name[4:] == auditfields[0]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], now.date().tointeger())
    aufield = [prop.name for prop in obj.__class__._descriptor.builders \
      if prop.name[4:] == auditfields[1]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], now.time().tointeger())
    aufield = [prop.name for prop in obj.__class__._descriptor.builders \
      if prop.name[4:] == auditfields[2]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], user)

  def getBusinessObjectProxy(self):
    return getBOProxy()

  @classmethod
  def createInstance(cls, pool, module):
    obj = object.__new__(cls)
    obj.__init__(pool)
    return obj

  @classmethod
  def instantiate(cls):
    obj = object.__new__(cls)
    obj.__init__(None)
    return obj

def getBOProxy():
  return BusinessObjectLocalService('__BOBJPROXY__')


