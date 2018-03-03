import sys
import copy
import string
import fakeapi
import ecfexceptions
import elixir as el
from countermeta import CounterMeta
from sqlalchemy.types import TypeEngine
from procsvc import getBOProxy
from jitutil import *

_moduleClassList = {}
_classPool = {}
_services = {}
_groups = {}

__all__= ('RPCService', 'RPCProperty', 'RPCMethod', 'RPCDatasetMethod', 'RPCParam', 'RPCField',
          'APIService', 'APILocalService', 'APIPool', 'APIInvocationService', 'RPCTypeInput',
          'RPCTypeOutput', 'RPCTypeInputOutput')

rpcs = list()

RPCTypeInput = 0
RPCTypeOutput = 1
RPCTypeInputOutput = 2

options_defaults = dict(
  inheritance='single',
  polymorphic=False,
  rpcname=None,
  allowcoloverride=False
  )

actions_type = dict(
  S='select',
  I='insert',
  U='update',
  D='delete'
  )

class APIService(object):

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
    raise ecfexceptions.ECFAPIServiceNotAvailable("%s -- %s: %s"%(origin,description,details))

class APILocalService(APIService):
  def __init__(self, name):
    self._name = name
    svc = _services[name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

class APIInvocationService(APIService):
  def __init__(self):
    self._name = '__API__'
    svc = _services[self._name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

class APIPool(APIService):
  def __init__(self):
    self._objPool = {}
    super(APIPool, self).__init__("__APIPROXY__")
    self.joinGroup("__APISVC__")
    self.exportMethod(self._exportedMethods)
    self.exportMethod(self.objectList)
    self.exportMethod(self.objectStatus)
    self.exportMethod(self.methodList)
    self.exportMethod(self.methodStatus)
    self.exportMethod(self.fieldList)
    self.exportMethod(self.fieldStatus)
    self.exportMethod(self.execMethod)
    self.exportMethod(self.getSession)

  def objectStatus(self, obj):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      return (obj, getattr(object, '_description', None), getattr(object, '_active', True))
    return None

  def objectList(self):
    return tuple([self.objectStatus(nm) \
                    for nm in self._objPool.keys()])

  def getObject(self, obj):
    ob = self._objPool.get(obj)
    if not ob:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      if not getattr(ob, '_active', True):
        self.abortResponse('Object Error', 'warning',
        'Object %s is not active' % str(obj))
      else:
        return ob.instantiate()
    return None


  def methodList(self, obj):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      return object.__getmethoddefs__()
    return None

  def methodStatus(self, obj, method):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      return object.__getmethodstat__(method)
    return None

  def fieldList(self, obj, method):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      return object.__getfielddefs__(method)
    return None

  def fieldStatus(self, obj, method, field):
    object = self._objPool.get(obj)
    if not object:
      self.abortResponse('Object Error', 'warning',
        'Object %s does not exist' % str(obj))
    else:
      return object.__getfielddef__(method, field)
    return None

  def execMethod(self, obj, method, *args):
    object = self.getObject(obj)
    try:
      ret = object.__execmethod__(method, *args)
    finally:
      el.session.close()
    return ret

  def add(self, name, objInstance):
    if self._objPool.has_key(name):
      del self._objPool[name]
    self._objPool[name] = objInstance

  def get(self, name):
    return self._objPool.get(name, None)

  def instanciate(self, module):
    return [klass.createInstance(self, module) \
              for klass in _moduleClassList.get(module, [])]

  def getSession(self, obj):
    ob = self.getObject(obj)
    return ob.__getsession__()

class RPCFieldProperty(object):
  __metaclass__ = CounterMeta

  def __init__(self):
    self.method = None
    self.name = None

class RPCParam(RPCFieldProperty):

  def __init__(self, paramname, description):
    super(RPCParam, self).__init__()
    self.name = paramname
    self.description = description

class RPCField(RPCFieldProperty):

  def __init__(self, name, ftype, type, description, **kwargs):
    super(RPCField, self).__init__()
    self.name = name
    if isinstance(type, TypeEngine):
      self.type = type
    else:
      atype = object.__new__(type)
      atype.__init__()
      self.type = atype
    self.ftype = ftype
    self.description = description
    self.required = kwargs.pop('required', False)
    self.kwargs = kwargs

class RPCProperty(object):

  __metaclass__ = CounterMeta

  def __init__(self, *args, **kwargs):
    self.rpc = None
    self.name = None
    self.active = kwargs.pop('active', True)

  def attach(self, rpc, name):
    self.rpc = rpc
    self.name = name
    rpc._descriptor.builders.append(self)

class GenericProperty(RPCProperty):
  def __init__(self, prop):
      super(GenericProperty, self).__init__()
      self.prop = prop

  def create_properties(self):
      if callable(self.prop):
          prop_value = self.prop(self.entity.table.c)
      else:
          prop_value = self.prop
      prop_value = self.evaluate_property(prop_value)
      self.rpc._descriptor.add_property(self.name, prop_value)

  def evaluate_property(self, prop):
      return prop

class RPCMethod(RPCProperty):

  def __init__(self, desc, *args, **kwargs):
    super(RPCMethod, self).__init__(*args, **kwargs)
    self.description = desc
    self.methodname = kwargs.pop('methodname', None)
    self.active = kwargs.pop('active', True)
    if self.methodname is not None:
      self.methodname = self.methodname.upper()
    self.parameters = list()
    for param in args:
      if isinstance(param, RPCParam):
        if self.get_param(param.name) is not None:
          raise Exception("parameter '%s' already exist in '%s' ! " %
                            (param.name, self.__name__))
        else:
          self.parameters.append(param)
    for param in self.parameters:
      setattr(self, param.name, param)
    self.kwargs = kwargs

  def attach(self, rpc, name):
    if self.methodname is None:
      self.methodname = name.upper()
    super(RPCMethod, self).attach(rpc, name)

  def get_param(self, key):
    for param in self.parameters:
      if key == param.name:
        return param
    return None

class RPCDatasetMethod(RPCProperty):

  def __init__(self, desc, *args, **kwargs):
    super(RPCDatasetMethod, self).__init__(*args, **kwargs)
    self.description = desc
    self.methodname = kwargs.pop('methodname', None)
    if self.methodname is not None:
      self.methodname = self.methodname.upper()
    self.fields = list()
    for field in args:
      if isinstance(field, RPCField):
        if self.get_field(field.name) is not None:
          raise Exception("field '%s' already exist in '%s' ! " %
                            (field.name, self.__name__))
        else:
          self.fields.append(field)
    for field in self.fields:
      setattr(self, field.name, field)
    self.kwargs = kwargs

  def attach(self, rpc, name):
    if self.methodname is None:
      self.methodname = name.upper()
    super(RPCDatasetMethod, self).attach(rpc, name)

  def get_field(self, key):
    for param in self.fields:
      if key == param.name:
        return param
    return None

class RPCSession(object):

  def __init__(self, controller):
    self.cookies = {}
    self.inputDataset = None
    self.outputDataset = None
    self.program = controller._descriptor.rpcname

  def getCookies(self):
    cookies = [(key, value) for key, value in self.cookies.iteritems()]
    tpcookies = sorted(cookies, key=lambda i: i[0])
    return tuple(tpcookies)

  def setCookies(self, cookies):
    for key, value in cookies:
      self.cookies[key] = value


class RPCDescriptor(object):
  '''
  RPCDescriptor describes columns and options needed for PGM creation.
  '''

  def __init__(self, rpc, name):
    self.rpc = rpc
    #self.module = sys.modules[rpc.__module__]
    module = str(rpc)[6:]
    module = module[:len(module)-1]
    module = module.split('.')[0][2:]
    self.module = module
    self.builders = []
    self.parent = None
    self.children = []
    for base in rpc.__bases__:
      if issubclass(base, RPCService) and base is not RPCService:
        if self.parent:
          raise Exception('%s rpc inherits from several rpcs,'
            ' and this is not supported.'
            % self.rpc.__name__)
        else:
          self.parent = base
          self.parent._descriptor.children.append(rpc)
    self.properties = dict()
    for option in options_defaults.keys():
      setattr(self, option, options_defaults[option])

    self.collection = getattr(self.module, '__rpc_collection__',
                                  rpcs)
    _moduleClassList.setdefault(self.module, []).append(rpc)
    _classPool[name] = rpc

  def add_property(self, name, property, check_duplicate=True):
    if check_duplicate and name in self.properties:
        raise Exception("property '%s' already exist in '%s' ! " %
                        (name, self.rpc.__name__))
    self.properties[name] = property

  def get_method(self, methodname):
    for method in self.builders:
      if method.methodname == methodname:
        return method
    return None

  def setup_options(self):
    '''
    Setup any values that might depend on using_options. For example, the
    rpcname.
    '''
    if self.collection is not None:
      self.collection.append(self.rpc)

    rpc = self.rpc
    if self.inheritance == 'concrete' and self.polymorphic:
      raise NotImplementedError("Polymorphic concrete inheritance is "
                                  "not yet implemented.")

    if self.parent:
      if self.inheritance == 'single':
        self.rpcname = self.parent._descriptor.rpcname

    if not self.rpcname:
      self.rpcname = rpc.__name__.upper()
    elif callable(self.rpcname):
        self.rpcname = self.rpcname (rpc)


def _is_rpc(class_):
  return isinstance(class_, RPCMeta)

class RPCMeta(type):
  """
  Form meta class.
  You should only use this if you want to define your own base class for your
  entities (ie you don't want to use the provided 'Entity' class).
  """
  _rpcs = {}

  def __init__(cls, name, bases, dict_):
    # only process subclasses of Form, not Form itself
    if bases[0] is object:
        return

    # build a dict of entities for each frame where there are entities
    # defined
    caller_frame = sys._getframe(1)
    cid = cls._caller = id(caller_frame)
    caller_rpcs = RPCMeta._rpcs.setdefault(cid, {})
    caller_rpcs[name] = cls

    # Append all rpcs which are currently visible by the rpc. This
    # will find more entities only if some of them where imported from
    # another module.
    for rpc in [e for e in caller_frame.f_locals.values()
                     if _is_rpc(e)]:
        caller_rpcs[rpc.__name__] = rpc

    # create the rpc descriptor
    desc = cls._descriptor = RPCDescriptor(cls, name)

    # Process attributes (using the assignment syntax), looking for
    # 'Property' instances and attaching them to this rpc.
    properties = [(name, attr) for name, attr in dict_.iteritems()
                               if isinstance(attr, RPCProperty)]
    sorted_props = sorted(properties, key=lambda i: i[1]._counter)

    for name, prop in sorted_props:
        prop.attach(cls, name)

    # setup misc options here (like rpcname etc.)
    desc.setup_options()

  def __call__(cls, *args, **kwargs):
    return type.__call__(cls, *args, **kwargs)


class RPCService(object):
  """
  The base class for all RPCs

  All RPC invocation service should inherit from this class. Statement can
  appear within the body of the definition of an rpc to define its
  fields, and other options.

  Here is an example:

    class HRM001MI(RPCService):
      _description = 'Manage Employee RPC'

      plainMethod = RPCMethod(
                          'A plain method example',
                          methodname='PLAINMETHOD',
                          RPCParams('param1', 'parameter description'),
                          RPCParams('param2', 'another param description'),
                          )

      manageEmployee = RPCDatasetMethod(
                          'Method for managing employee',
                          methodname='MANAGEEMPLOYEE'
                          RPCField('EMPID', InputOutputField, Integer, 'Employee ID'),
                          RPCField('EMPNM', InputField, String(48), 'Employee Full Name'),
                          )

      def plainMethod_method(param1, param2):
        ...

      def manageEmployee_select(input, output):
        ...

      def manageEmployee_insert(input):
        ...

      def manageEmployee_update(input):
        ...

      def manageEmployee_delete(input):
        ...

  """
  __metaclass__ = RPCMeta

  def __init__(self, pool):
    if pool is not None:
      pool.add(self._descriptor.rpcname, self)
      self.pool = pool
    else:
      self.pool = None

  def createInstance(cls, pool, module):
    obj = object.__new__(cls)
    obj.__init__(pool)
    return obj

  createInstance = classmethod(createInstance)

  def instantiate(cls):
    obj = object.__new__(cls)
    obj.__init__(None)
    return obj

  instantiate = classmethod(instantiate)

  def getBusinessObjectProxy(self):
    return getBOProxy()

  def __getmethodstat__(self, method):
    if not isinstance(method, RPCProperty):
      method = self._descriptor.get_method(method)
    if isinstance(method, RPCProperty):
      stat = list()
      mt = None
      if isinstance(method, RPCMethod):
        mt = 'P'
        xmethod = '%s_exec' % method.name.lower()
        if hasattr(self, xmethod):
          stat.append('X')
      elif isinstance(method, RPCDatasetMethod):
        mt = 'D'
        for xm in actions_type.keys():
          xmethod = '%s_%s' % (method.name.lower(), actions_type[xm])
          if hasattr(self, xmethod):
            stat.append(xm)
      return (method.methodname, method.description, mt, getattr(method, 'active', True), string.join(stat,''))
    else:
      raise Exception("method %s could not be found" % str(method))
    return None

  def __getmethoddefs__(self):
    ret = list()
    for meth in self._descriptor.builders:
      ret.append(self.__getmethodstat__(meth))
    return tuple(ret)

  def __getfielddefs__(self, methodname):
    ret = list()
    method = self._descriptor.get_method(methodname)
    if method:
      if isinstance(method, RPCMethod):
        for param in method.parameters:
          ret.append((param.name, param.description))
      elif isinstance(method, RPCDatasetMethod):
        for field in method.fields:
          ret.append(
            (
            field.name,
            field.description,
            field.ftype,
            field.type.get_ecf_type(fakeapi),
            getattr(field.type,'length', 0),
            getattr(field.type,'precision', 0),
            getattr(field.type,'scale', 0),
            field.required
            ))
      return tuple(ret)
    else:
      raise Exception("method %s could not be found" %methodname)
    return None

  def __getfielddef__(self, methodname, fieldname):
    ret = ()
    method = self._descriptor.get_method(methodname)
    if method:
      if isinstance(method, RPCMethod):
        for param in method.parameters:
          if (param.name == fieldname):
            ret = (param.name, param.description)
      elif isinstance(method, RPCDatasetMethod):
        for field in method.fields:
          if (field.name == fieldname):
            ret = (
              field.name,
              field.description,
              field.ftype,
              field.type.get_ecf_type(fakeapi),
              getattr(field.type,'length', 0),
              getattr(field.type,'precision', 0),
              getattr(field.type,'asdecimal', 0),
              field.required
              )
      return ret
    else:
      raise Exception("method %s could not be found" %methodname)
    return None

  def __execpmethod__(self, method, *args):
    exec_meth = '%s_exec' % method.name.lower()
    if hasattr(self, exec_meth):
      return getattr(self, exec_meth)(*args)
    else:
      raise Exception("The implementation routine for method %s could not be found" %methodname)
    return None

  def __execdmethod__(self, method, type, *args):
    st = actions_type[type.upper()]
    exec_meth = '%s_%s' % (method.name.lower(), st)
    if hasattr(self, exec_meth):
      return getattr(self, exec_meth)(*args)
    else:
      raise Exception("The implementation routine for method %s could not be found" % exec_meth)
    return None

  def __execmethod__(self, methodname, *args):
    method = self._descriptor.get_method(methodname)
    if method and method.active:
      if isinstance(method, RPCMethod):
        return self.__execpmethod__(method, *args)
      elif isinstance(method, RPCDatasetMethod):
        return self.__execdmethod__(method, *args)
    else:
      raise Exception("method %s could not be found or is not active" %methodname)
    return None

  def __getsession__(self):
    return RPCSession(self)

def createAPILocalService(name):
  return APILocalService(name)

def getAPILocalService(name):
  return createAPILocalService(name)
