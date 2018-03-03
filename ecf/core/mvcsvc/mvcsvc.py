import sys
import copy
import types
import string
import ecfexceptions
import fakeapi
import elixir as el
import datetime as dt
from countermeta import CounterMeta
from mvcsvcutil import MVCClassMutator, process_mutators
from sqlalchemy.types import TypeEngine
from sqlalchemy import util as sautil
from procsvc import getBOProxy
from jitutil import *

_moduleClassList = {}
_classPool = {}
_services = {}
_groups = {}

__all__= ('MVCController', 'MVCField', 'MVCSession', 'MVCCommandText',
          'MVCService', 'MVCLocalService', 'MVCPool',
          'MVCTypeParam', 'MVCTypeList', 'MVCTypeField', 'MVCExtFunction', 'MVCLookupDef',
          'MVCExecUnknown', 'MVCExecShow', 'MVCExecCopy', 'MVCExecAppend', 'MVCExecEdit', 'MVCExecDelete', 'MVCExecSelect',
          'MVCFuncSelect', 'MVCFuncNew', 'MVCFuncOpen', 'MVCFuncShow', 'MVCFuncCopy', 'MVCFuncDelete', 'MVCModelBinder',
          'getMVCLocalService', 'ecNormal', 'ecUpperCase', 'ecLowerCase')

mvcs = list()

MVCTypeParam = 1
MVCTypeList = 2
MVCTypeField = 4

MVCExecUnknown = 0
MVCExecShow = 1
MVCExecCopy = 2
MVCExecAppend = 3
MVCExecEdit = 4
MVCExecDelete = 5
MVCExecSelect = 6

MVCFuncSelect = 0
MVCFuncNew = 1
MVCFuncOpen = 2
MVCFuncShow = 3
MVCFuncCopy = 4
MVCFuncDelete = 5

ecNormal = 0
ecUpperCase = 1
ecLowerCase = 2

options_defaults = dict(
  inheritance='single',
  polymorphic=False,
  mvcname=None,
  allowcoloverride=False
  )

class MVCService(object):

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
    raise ecfexceptions.ECFMVCServiceNotAvailable("%s -- %s: %s"%(origin,description,details))

class MVCLocalService(MVCService):

  def __init__(self, name):
    self._name = name
    svc = _services[name]
    for proc in svc._methods:
      setattr(self, proc, svc._methods[proc])

class MVCPool(MVCService):

  def __init__(self):
    self._objPool = {}
    super(MVCPool, self).__init__('__MVCPROXY__')
    self.joinGroup('__MVCSVC__')
    self.exportMethod(self._exportedMethods)
    self.exportMethod(self.objectList)
    self.exportMethod(self.objectStatus)
    self.exportMethod(self.fieldList)
    self.exportMethod(self.execMethod)
    self.exportMethod(self.getSession)
    self.exportMethod(self.initView)
    self.exportMethod(self.openView)
    self.exportMethod(self.retrieveData)
    self.exportMethod(self.printData)
    self.exportMethod(self.postData)
    self.exportMethod(self.finalizeView)
    self.exportMethod(self.synchronizeData)
    self.exportMethod(self.lookupView)

  def objectStatus(self, obj):
    """Get the object status"""
    ob = self._objPool.get(obj)
    if not ob:
      self.abortResponse('Object Error', 'warning',
        'MVC Object %s does not exist' % str(obj))
    return (obj, getattr(ob, '_description', None), getattr(ob, '_active', True))

  def getClass(self, mod):
    return self._objPool.get(mod)

  def objectList(self):
    return tuple([self.objectStatus(nm) for nm in self._objPool.keys()])

  def getObject(self, obj):
    ob = self._objPool.get(obj)
    if not ob:
      self.abortResponse('Object Error', 'warning',
        'MVC Object %s does not exist' % str(obj))
    elif not getattr(ob, '_active', True):
      self.abortResponse('Object Error', 'warning',
      'MVC Object %s is not active' % str(obj))
    else:
      return ob.instantiate()
    return None

  def fieldList(self, obj):
    ob = self.getObject(obj)
    return ob.__getfielddefs__()

  def getSession(self, obj):
    ob = self.getObject(obj)
    return ob.__getsession__()

  def initView(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.initView(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def openView(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.openView(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def retrieveData(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.retrieveData(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def printData(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.printData(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def postData(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.postData(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def finalizeView(self, obj, session):
    ob = self.getObject(obj)
    try:
      ret = ob.finalizeView(session)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def lookupView(self, obj, *args):
    ob = self.getObject(obj)
    try:
      ret = ob.lookupView(*args)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def synchronizeData(self, obj, session, fieldName, fieldType):
    ob = self.getObject(obj)
    try:
      ret = ob.synchronizeData(session, fieldName, fieldType)
      if ret == None:
        ret = session
    finally:
      el.session.close()
    return ret

  def execMethod(self, obj, method, session, *args):
    ob = self.getObject(obj)
    try:
      ret = ob.__execmethod__(method, session, *args)
      if ret == None:
        ret = session
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
    classList = _moduleClassList.get(module, [])
    return [klass.createInstance(self, module) for klass in classList]

class MVCFieldProperty(object):

  def __init__(self):
    self.fieldNo = 0
    self.type = None
    self.ftype = None
    self.name = None
    self.label = None
    self.tlabel = None
    self.required = False
    self.enabled = True
    self.visible = True
    self.readOnly = False
    self.updateable = True
    self.primaryKey = False
    self.kwargs = None
    self.synchronized = False
    self.browseable = False
    self.charcase = ecNormal
    self.choices = {}

  def copyProperties(self, props):
    self.fieldNo = props.fieldNo
    self.type = props.type
    self.ftype = props.ftype
    self.name = props.name
    self.label = props.label
    self.tlabel = props.tlabel
    self.required = props.required
    self.enabled = props.enabled
    self.visible = props.visible
    self.readOnly = props.readOnly
    self.updateable = props.updateable
    self.synchronized = props.synchronized
    self.browseable = props.browseable
    self.charcase = props.charcase
    self.primaryKey = props.primaryKey
    if props.kwargs:
      self.kwargs = props.kwargs.copy()
    else:
      self.kwargs = None
    if props.choices:
      self.choices = props.choices.copy()
    else:
      self.choices = {}

  def getFieldDef(self):
    tpchoice = sorted([(key, value) for key, value in self.choices.iteritems()],
        key=lambda i: i[1])
    return (
        self.fieldNo,
        self.name,
        self.tlabel,
        self.ftype,
        self.type.get_ecf_type(fakeapi),
        getattr(self.type,'length', 0),
        getattr(self.type,'precision', 0),
        getattr(self.type,'scale', 0),
        self.primaryKey,
        self.required,
        self.enabled,
        self.visible,
        self.readOnly,
        tuple(tpchoice),
        self.synchronized,
        self.browseable,
        self.charcase,
        self.updateable
        )


class MVCField(object):
  """
  Represents the definition of a 'field' on an mvc class.
  This class represents a column on the table where the entity is stored.

  Parameters required for object construction:
      ftype: field type (MVCTypeField, MVCTypeList, or/and MVCTypeParam)
      type:  Datatype (String, Numeric, Date, Time)
  Args:
      label: identify label for this field
      required: identify that value entered in this field is required, thus it must not empty
      enabled: identify the field is enabled for editing
      visible: set the field visibility on client
      browseable: identify if data on this field could be retrieved from lookup browser
      synchronized: identify any modification made on this field must be synchronized by server
      charcase: identify input charcase type (ecUpperCase, ecLowerCase)
      choices: set the multiple choice for this field (usually shown by a combo box control)
      updateable: set if this field updateable into persistent media (table)
  """

  __metaclass__ = CounterMeta

  def __init__(self, ftype, type, **kwargs):
    '''
    Construct the field object on an mvc class

    Parameters:
      ftype: field type (MVCTypeField, MVCTypeList, or/and MVCTypeParam)
      type:  Datatype (String, Numeric, Date, Time)
    Args:
      label: identify label for this field
      required: identify that value entered in this field is required, thus it must not empty
      enabled: identify the field is enabled for editing
      visible: set the field visibility on client
      browseable: identify if data on this field could be retrieved from lookup browser
      synchronized: identify any modification made on this field must be synchronized by server
      charcase: identify input charcase type (ecUpperCase, ecLowerCase)
      choices: set the multiple choice for this field (usually shown by a combo box control)
      updateable: set if this field updateable into persistent media (table)
    '''

    self.properties = MVCFieldProperty()
    if isinstance(type, TypeEngine):
      self.properties.type = type
    else:
      atype = object.__new__(type)
      atype.__init__()
      self.properties.type = atype
    self.properties.ftype = ftype
    self.properties.label = kwargs.pop('label', None)
    self.properties.required = kwargs.pop('required', False)
    self.properties.enabled = kwargs.pop('enabled', True)
    self.properties.visible = kwargs.pop('visible', True)
    self.properties.readOnly = kwargs.pop('readOnly', False)
    self.properties.synchronized = kwargs.pop('synchronized', False)
    self.properties.browseable = kwargs.pop('browseable', False)
    self.properties.charcase = kwargs.pop('charcase', ecNormal)
    self.properties.updateable = kwargs.pop('updateable', True)
    choice = kwargs.pop('choices', {})
    choice_type = sautil.duck_type_collection(choice)
    if choice and (choice_type == types.ListType or choice == types.TupleType):
      for itval in choice:
        self.properties.choices[itval] = itval
    else:
      if (choice_type == types.DictType):
        self.properties.choices = choice.copy()
    self.properties.primaryKey =  kwargs.pop('primaryKey', False)
    self.properties.kwargs = kwargs

  def attach(self, controller, name):
    self.properties.name = name
    self.properties.fieldNo = self._counter
    controller._descriptor.fields.append(self)

class MVCObject(object):
  pass

@nativeclass
class MVCModelBinder(object):

  def __init__(self, model):
    self.model = model

  def getFields(self, pkType = 0):
    aret = []
    if self.model <> None:
      for prop in self.model._descriptor.columns:
        if (pkType in (1, 2, 3)):
          if (prop.primary_key == True) and (pkType == 1):
            aret.append(prop.name)
          elif (prop.primary_key != True) and (pkType == 2):
            aret.append(prop.name)
          elif ((prop.primary_key == True) or \
               ((prop.nullable == False))) and \
               (pkType == 3):
            aret.append(prop.name)
        else:
          aret.append(prop.name)
    return aret

  def getPKFields(self):
    return self.getFields(1)

  def getFieldList(self, mvcsession, ftype):
    return [attr[1] for attr in mvcsession.getFieldDefs() \
        if ((attr[3] | ftype) == attr[3])]

  def getUpdateableFieldList(self, mvcsession, ftype):
    return [attr[1] for attr in mvcsession.getFieldDefs() \
        if ((attr[3] | ftype) == attr[3]) and (attr[17] == True)]

  def getObjList(self, mvcsession, initparm_method):
    proxy = getBOProxy()
    usrobj = proxy.getObject('USROBJ')
    sysobj = proxy.getObject('SYSOBJ')
    info = usrobj.retrieveUserInfo(mvcsession)
    cono = info[2]
    if cono is None:
      cono = ''
    mvcsession.cookies['cono'] = cono
    if self.model <> None:
      if (mvcsession.paramDataset.IsActive == True):
        oldvalues = None
        if (mvcsession.paramDataset.RecordCount != 0):
          oldvalues = mvcsession.paramDataset.FieldsAsDict()
        _dict = sysobj.getPGMVar(cono, mvcsession)
        if (len(_dict) > 0):
          if oldvalues:
            mvcsession.paramDataset.Edit()
            for key, value in _dict.iteritems():
              if (oldvalues.has_key(key) != True) or \
                 (oldvalues[key] is None):
                mvcsession.paramDataset.SetFieldValue(key, value[0])
          else:
            mvcsession.paramDataset.Append()
            for key, value in _dict.iteritems():
              mvcsession.paramDataset.SetFieldValue(key, value[0])
          mvcsession.paramDataset.Post()
      query = initparm_method(mvcsession, self.model.query)
      sysobj.setPGMVar(cono, mvcsession)
      objs = query.all()
      if objs:
        fields = self.getFieldList(mvcsession, MVCTypeList)
        fieldlist = ";".join(fields)
        mvcsession.listDataset.CopyFromORMList(fieldlist, fieldlist, objs)

  def setAuditFields(self, mvcsession, obj):
    auditfields = ['AUDT', 'AUTM', 'AUUS']
    now = dt.datetime.now()
    fields = self.getFields()
    aufield = [aufld for aufld in fields if aufld[4:] == auditfields[0]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], now.date().tointeger())
    aufield = [aufld for aufld in fields if aufld[4:] == auditfields[1]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], now.time().tointeger())
    aufield = [aufld for aufld in fields if aufld[4:] == auditfields[2]]
    if len(aufield) > 0:
      setattr(obj, aufield[0], mvcsession.cookies['user_name'].encode('utf8'))

  def getRecord(self, mvcsession, callback_methods):
    if (self.model <> None) and (mvcsession.execType <> MVCExecAppend):
      fields = mvcsession.listDataset.FieldsAsDictExt()
      pkfields = self.getPKFields()
      try:
        values = [fields[pk] for pk in pkfields]
      except:
        raise Exception("Some of required primary key field is not included as list type field")
      obj = self.model.get(tuple(values))
      if obj:
        fields = self.getFieldList(mvcsession, MVCTypeField)
        if (mvcsession.execType == MVCExecCopy):
          pkfields = self.getPKFields()
          pfields = [fld for fld in fields if (fld not in pkfields)]
          fields = pfields
        fieldlist = ";".join(fields)
        mvcsession, obj = callback_methods[1](mvcsession, obj)
        mvcsession.entryDataset.CopyFromORM(fieldlist, fieldlist, obj)
        if (mvcsession.execType == MVCExecEdit):
          pkType = 1
          fields = self.getFields(pkType)
          for field in fields:
            if getattr(mvcsession.fieldDefs, field, None) <> None:
              getattr(mvcsession.fieldDefs, field).enabled = False
        mvcsession, obj = callback_methods[2](mvcsession, obj)
      else:
        raise Exception("record could not be found")
    elif (self.model <> None) and (mvcsession.execType == MVCExecAppend):
      callback_methods[0](mvcsession)

  def setRecord(self, mvcsession, callback_methods):
    if self.model <> None:
      # call validate first on callback[0]
      callback_methods[0](mvcsession)
      if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
        obj = object.__new__(self.model)
        obj.__init__()
        if obj:
          # call before post
          mvcsession, obj = callback_methods[1](mvcsession, obj)
          fields = self.getFieldList(mvcsession, MVCTypeField)
          fieldlist = ";".join(fields)
          mvcsession.entryDataset.CopyIntoORM(fieldlist, fieldlist, obj)
          self.setAuditFields(mvcsession, obj)
          if not el.session.transaction_started():
            el.session.begin()
          try:
            notnullfields = self.getFields(3)
            for field in notnullfields:
              if getattr(obj, field, None) is None:
                aprop = mvcsession.getFieldProperty(field)
                exceptfld = field if aprop is None else aprop.label
                raise Exception("Empty value for field '%s' is not acceptable" % exceptfld)
            # make sure there are no duplicate record exist
            pkfields = self.getFields(1)
            if len(pkfields) > 1:
              values = tuple([getattr(obj, field, None) for field in pkfields \
                  if hasattr(obj, field)])
            else:
              values = getattr(obj, pkfields[0], None) if hasattr(obj, pkfields[0]) else None
            dupl = self.model.get(values)
            if dupl:
              raise Exception("Duplicate record is found, could not continue")
            # save the record
            el.session.add(obj)
            el.session.commit()
          except:
            el.session.rollback()
            raise
          # call after post
          mvcsession, obj = callback_methods[2](mvcsession, obj)
      elif mvcsession.execType == MVCExecEdit:
        fields = mvcsession.entryDataset.FieldsAsDictExt()
        pkfields = self.getPKFields()
        values = [fields[pk] for pk in pkfields]
        obj = self.model.get(tuple(values))
        if obj:
          # call before post
          mvcsession, obj = callback_methods[1](mvcsession, obj)
          fieldlist = ";".join(self.getUpdateableFieldList(mvcsession, MVCTypeField))
          mvcsession.entryDataset.CopyIntoORM(fieldlist, fieldlist, obj)
          self.setAuditFields(mvcsession, obj)
          if not el.session.transaction_started():
            el.session.begin()
          try:
            # make sure there are no empty field on PK and not nullable field exist
            notnullfields = self.getFields(3)
            for field in notnullfields:
              if getattr(obj, field, None) is None:
                aprop = mvcsession.getFieldProperty(field)
                exceptfld = field if aprop is None else aprop.label
                raise Exception("Empty value for field '%s' is not acceptable" % exceptfld)
            el.session.update(obj)
            el.session.commit()
          except:
            el.session.rollback()
            raise
          # call after post
          mvcsession, obj = callback_methods[2](mvcsession, obj)
      elif mvcsession.execType == MVCExecDelete:
        fields = mvcsession.entryDataset.FieldsAsDictExt()
        values = [fields[pk] for pk in self.getPKFields()]
        obj = self.model.get(tuple(values))
        if obj:
          mvcsession, obj = callback_methods[1](mvcsession, obj)
          if not el.session.transaction_started():
            el.session.begin()
          try:
            el.session.delete(obj)
            el.session.commit()
          except:
            el.session.rollback()
            raise
          mvcsession, obj = callback_methods[2](mvcsession, obj)
        else:
          raise Exception("Record is lost, probably it has been deleted by other user")


class MVCExtFunction(object):

  def __init__(self, label, method, **kwargs):
    self.params = kwargs.pop('params', {})
    self.autoSelect = kwargs.pop('autoSelect', False)
    self.confirmMessage = kwargs.pop('confirmMessage', None)
    self.label = label
    if callable(method):
      self.commandType = 'INTERNAL'
      self.commandText = method.__name__
    else:
      self.commandType = 'VIEW'
      self.commandText = method

  def getParams(self):
    return tuple(sorted([(key, value) for key, value in self.params.iteritems()],
        key=lambda i: i[1]))

class MVCLookupDef(object):
  """
  Provide Lookup definition into a specific program for an entry field
  example:
    ret = MVCLookupDef('CMN100','CMCPCONO',
            params = {'PARAMFLD':'%v:some value'
                'PARAMFLD':'%f:SRCFIELD'}
            extassign = {'SOMEFIELD':'%v:some value'
                'OTHERFIELD':'%f:SRCFIELD'
              })
  """

  def __init__(self, svcname, retfield, **kwargs):
    self.params = kwargs.pop('params', {})
    self.svcname = svcname
    self.retfield= retfield
    self.extassignment=kwargs.pop('extassign', {})

  def setup(self, svcname, retfield, **kwargs):
    self.svcname = svcname
    self.retfield= retfield
    self.params = kwargs.pop('params', {})
    self.extassignment=kwargs.pop('extassign', {})

  def getParams(self):
    return tuple(sorted([(key, value) for key, value in self.params.iteritems()],
        key=lambda i: i[1]))

  def getExtAssigment(self):
    return tuple(sorted([(key, value) for key, value in self.extassignment.iteritems()],
        key=lambda i: i[1]))

class MVCCommandText(object):

  def __init__(self, session):
    self.params = dict()
    self.commandType = 'INTERNAL'
    self.command = None

  def execMethod(self, method):
    if callable(method):
      self.command = method.__name__
      self.commandType = 'INTERNAL'

  def execView(self, view):
    self.command = view
    self.commandType = 'VIEW'

  def setParam(self, key, value):
    self.params[key] = value

  def getParam(self, key):
    return self.params[key]

  def getParams(self):
    return tuple(sorted([(key, value) for key, value in self.params.iteritems()],
        key=lambda i: i[1]))

  def copyFrom(self, objcpy):
    self.params = copy.deepcopy(objcpy.params)
    self.commandType = copy.deepcopy(objcpy.commandType)
    self.command = copy.deepcopy(objcpy.command)
    return self

class MVCSession(object):

  def __init__(self, controller):
    import ecflocale as ecf
    self.cookies = {}
    self.fieldDefs = MVCObject()
    self.pageDefs = getattr(controller, '_pages', ())
    self.supportedFuncs = getattr(controller, '_supported_functions', ())
    self.execType = MVCExecUnknown
    self.paramDataset = None
    self.entryDataset = None
    self.listDataset = None
    self.program = controller._descriptor.mvcname
    self.page = None
    self.extFunctions = None
    self.selectFunction = None
    self.commandText = MVCCommandText(self)

    # copy default field properties
    _binder = getattr(controller, '_model_binder', None)
    try:
      for field in controller._descriptor.fields:
        if not hasattr(self.fieldDefs, field.properties.name):
          setattr(self.fieldDefs, field.properties.name, MVCFieldProperty())
        aprops = getattr(self.fieldDefs, field.properties.name)
        aprops.copyProperties(field.properties)
        if (aprops.tlabel is None):
          if aprops.label is not None:
            aprops.tlabel = ecf.locale.translate(controller._descriptor.mvcname, aprops.label)
          if (aprops.tlabel is None) and (_binder is not None):
            fieldprops = [prop for prop in _binder.model._descriptor.builders \
              if (prop.name == field.properties.name)]
            if len(fieldprops) > 0:
              aprops.tlabel = ecf.locale.translate(controller._descriptor.mvcname, fieldprops[0].label)
              if aprops.tlabel is None:
                aprops.tlabel = fieldprops[0].label
              if aprops.label is None:
                aprops.label = fieldprops[0].label
          if (aprops.tlabel is None) and (aprops.label is not None):
            aprops.tlabel = aprops.label
    finally:
      el.session.close()


  def getFieldProperty(self, fldname):
    aret = None
    if hasattr(self.fieldDefs, fldname):
      aret = getattr(self.fieldDefs, fldname, None)
    return aret

  def getFields(self):
    field_dict = self.fieldDefs.__dict__
    fields = [(name, attr) for name, attr in field_dict.iteritems()
                               if isinstance(attr, MVCFieldProperty)]
    sorted_fields = sorted(fields, key=lambda i: i[1].fieldNo)
    return sorted_fields

  def getFieldDefs(self):
    ret = list()
    sorted_fields = self.getFields()
    for name, field in sorted_fields:
        ret.append(field.getFieldDef())
    return ret

  def getCookies(self):
    return tuple(sorted([(key, value) for key, value in self.cookies.iteritems()],
        key=lambda i: i[0]))

  def setFields(self, lstField, lstProps, value):
    for fld in lstField:
      for prop in lstProps:
        setattr(getattr(self.fieldDefs, fld), prop, value)

  def setCookies(self, cookies):
    for key, value in cookies:
      self.cookies[key] = value

  def copySession(self, objcpy):
    self.execType = copy.deepcopy(objcpy.execType)
    self.cookies = copy.deepcopy(objcpy.cookies)
    self.paramDataset = objcpy.paramDataset
    self.entryDataset = objcpy.entryDataset
    self.listDataset = objcpy.listDataset
    self.program = copy.deepcopy(objcpy.program)
    self.page = copy.deepcopy(objcpy.page)
    self.supportedFuncs = copy.deepcopy(objcpy.supportedFuncs)
    self.commandText = copy.deepcopy(objcpy.commandText)
    self.printID = copy.deepcopy(objcpy.printID)
    sorted_fields = objcpy.getFields()
    for name, field in sorted_fields:
      if not hasattr(self.fieldDefs, name):
        setattr(self.fieldDefs, name, MVCFieldProperty())
      getattr(self.fieldDefs, name).copyProperties(field)
    return self

class MVCDescriptor(object):
  '''
  MVCDescriptor describes columns and options needed for MVC creation.
  '''

  def __init__(self, mvc, name):
    self.mvc = mvc
    #self.module = sys.modules[mvc.__module__]
    module = str(mvc)[6:]
    module = module[:len(module)-1]
    module = module.split('.')[0][2:]
    self.module = module
    self.fields = []
    self.parent = None
    self.children = []
    for base in mvc.__bases__:
      if issubclass(base, MVCController) and base is not MVCController:
        if self.parent:
          raise Exception('%s mvc inherits from several mvcs,'
            ' and this is not supported.'
            % self.mvc.__name__)
        else:
          self.parent = base
          self.parent._descriptor.children.append(mvc)
    self.properties = dict()
    for option in options_defaults.keys():
      setattr(self, option, options_defaults[option])

    self.collection = getattr(self.module, '__mvc_collection__',
                                  mvcs)
    _moduleClassList.setdefault(self.module, []).append(mvc)
    _classPool[name] = mvc

  def add_property(self, name, property, check_duplicate=True):
    if check_duplicate and name in self.properties:
        raise Exception("property '%s' already exist in '%s' ! " %
                        (name, self.mvc.__name__))
    self.properties[name] = property

  def get_field(self, fieldname):
    for field in self.fields:
      if field.properties.name == fieldname:
        return field
    return None

  def setup_options(self):
    '''
    Setup any values that might depend on using_options. For example, the
    mvc.name.
    '''
    if self.collection is not None:
      self.collection.append(self.mvc)

    mvc = self.mvc
    if self.inheritance == 'concrete' and self.polymorphic:
      raise NotImplementedError("Polymorphic concrete inheritance is "
                                  "not yet implemented.")

    if self.parent:
      if self.inheritance == 'single':
        self.mvcname = self.parent._descriptor.mvcname
    if not self.mvcname:
      self.mvcname = mvc.__name__.upper()
    elif callable(self.mvcname):
      self.mvcname = self.mvcname (mvc)

    import ecflocale as ecf
    try:
      for field in self.fields:
        field.properties.tlabel = ecf.locale.translate(self.mvcname, \
          field.properties.label)
    finally:
      el.session.close()

def _is_mvc(class_):
  return isinstance(class_, MVCMeta)

class MVCMeta(type):

  _mvcs = {}

  def __init__(cls, name, bases, dict_):
    # only process subclasses of Form, not Form itself
    if bases[0] is object:
      return

    # build a dict of entities for each frame where there are entities
    # defined
    caller_frame = sys._getframe(1)
    cid = cls._caller = id(caller_frame)
    caller_mvcs = MVCMeta._mvcs.setdefault(cid, {})
    caller_mvcs[name] = cls

    # Append all mvcs which are currently visible by the mvc. This
    # will find more entities only if some of them where imported from
    # another module.
    for mvc in [e for e in caller_frame.f_locals.values()
                     if _is_mvc(e)]:
        caller_mvcs[mvc.__name__] = mvc

    # create the mvc descriptor
    desc = cls._descriptor = MVCDescriptor(cls, name)

    # Process attributes (using the assignment syntax), looking for
    # 'Property' instances and attaching them to this mvc.
    properties = [(name, attr) for name, attr in dict_.iteritems()
                               if isinstance(attr, MVCField)]
    sorted_props = sorted(properties, key=lambda i: i[1]._counter)

    for name, prop in sorted_props:
        prop.attach(cls, name)

    # process mutators
    process_mutators(cls)

    # setup misc options here (like mvcname etc.)
    desc.setup_options()

  def __call__(cls, *args, **kwargs):
    return type.__call__(cls, *args, **kwargs)

class MVCController(object):
  """
  The base class for all MVCs

  All MVC invocation service should inherit from this class. Statement can
  appear within the body of the definition of an mvc to define its
  fields, and other options.

  """
  __metaclass__ = MVCMeta

  def __init__(self, pool):
    if pool is not None:
      pool.add(self._descriptor.mvcname, self)
      self.pool = pool
    else:
      self.pool = None

  def hasModelBindery(self):
    return getattr(self, '_model_binder', None) is not None

  def getBusinessObjectProxy(self):
    return getBOProxy()

  def initView(self, mvcsession):
    return mvcsession

  def openView(self, mvcsession):
    if self.hasModelBindery():
      _binder = getattr(self, '_model_binder', None)
      _binder.getObjList(mvcsession, self.initializeParam)
    return mvcsession

  def retrieveData(self, mvcsession):
    if self.hasModelBindery():
      _binder = getattr(self, '_model_binder', None)
      _binder.getRecord(mvcsession,
        (self.initializeData, self.beforeRetrieveData, self.afterRetrieveData))
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    return mvcsession

  def postData(self, mvcsession):
    if self.hasModelBindery():
      _binder = getattr(self, '_model_binder', None)
      _binder.setRecord(mvcsession,
        (self.validateData, self.beforePostData, self.afterPostData))
    return mvcsession

  def printData(self, mvcsession):
    return getattr(self, '_print_id', None)

  def validateData(self, mvcsession):
    return mvcsession

  def beforeRetrieveData(self, mvcsession, obj):
    return (mvcsession, obj)

  def afterRetrieveData(self, mvcsession, obj):
    return (mvcsession, obj)

  def beforePostData(self, mvcsession, obj):
    return (mvcsession, obj)

  def afterPostData(self, mvcsession, obj):
    return (mvcsession, obj)

  def initializeData(self, mvcsession):
    return mvcsession

  def initializeParam(self, mvcsession, query):
    return query

  def finalizeView(self, mvcsession):
    return mvcsession

  def lookupView(self, mvcsession, fieldName):
    return MVCLookupDef('', '')

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

  @nativemethod
  def __getfielddefs__(self):
    import ecflocale as ecf
    ret = list()
    _binder = getattr(self, '_model_binder', None)
    try:
      for field in self._descriptor.fields:
        tpchoice =  [(key, value) for key, value in field.properties.choices.iteritems()]
        label = field.properties.tlabel
        if (field.properties.label is None) and (_binder is not None):
          fieldprops = [prop for prop in _binder.model._descriptor.builders \
            if (prop.name == field.properties.name)]
          if len(fieldprops) > 0:
            label = ecf.locale.translate(self._descriptor.mvcname, fieldprops[0].label)
        ret.append(
          (
          field.properties.name,
          label,
          field.properties.ftype,
          field.properties.type.get_ecf_type(fakeapi),
          getattr(field.properties.type,'length', 0),
          getattr(field.properties.type,'precision', 0),
          getattr(field.properties.type,'asdecimal', 0),
          field.properties.primaryKey,
          field.properties.required,
          field.properties.enabled,
          field.properties.visible,
          field.properties.readOnly,
          tuple(tpchoice),
          field.properties.synchronized,
          field.properties.browseable,
          field.properties.charcase,
          field.properties.updateable
          ))
    finally:
      el.session.close()
    return ret

  def __execmethod__(self, methodname, session, *args):
    exec_method = methodname
    if hasattr(self, exec_method):
      return getattr(self, exec_method)(session, *args)
    else:
      raise Exception('Method %s could not be found.' % methodname)

  def __getsession__(self):
    return MVCSession(self)

def createMVCLocalService(name):
  return MVCLocalService(name)

def getMVCLocalService(name):
  return createMVCLocalService(name)

