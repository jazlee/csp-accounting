from apisvc import APIService, APILocalService
from intsvc import INTService, INTLocalService
from mvcsvc import MVCService, MVCLocalService
from jobsvc import JOBService, JOBLocalService
from procsvc import BusinessObjectService, BusinessObjectLocalService
from jitutil import *

@nativeclass
class APIObjectsProxy(APIService):
  def __init__(self, name='__API__'):
    super(APIObjectsProxy, self).__init__(name)
    self.joinGroup('__APISVC__')
    self.exportMethod(self.objectList)
    self.exportMethod(self.objectStatus)
    self.exportMethod(self.methodList)
    self.exportMethod(self.methodStatus)
    self.exportMethod(self.fieldList)
    self.exportMethod(self.fieldStatus)
    self.exportMethod(self.getSession)
    self.exportMethod(self.execMethod)
    self.exportMethod(self.checkAPIAuth)

  def objectList(self):
    service = APILocalService('__APIPROXY__')
    res = service.objectList()
    return res

  def objectStatus(self, obj):
    service = APILocalService('__APIPROXY__')
    res = service.objectStatus(obj)
    return res

  def methodList(self, obj):
    service = APILocalService('__APIPROXY__')
    res = service.methodList(obj)
    return res

  def methodStatus(self, obj, method):
    service = APILocalService('__APIPROXY__')
    res = service.methodStatus(obj, method)
    return res

  def getSession(self, obj):
    service = APILocalService('__APIPROXY__')
    res = service.getSession(obj)
    return res

  def fieldList(self, obj, method):
    service = APILocalService('__APIPROXY__')
    res = service.fieldList(obj, method)
    return res

  def fieldStatus(self, obj, method, field):
    service = APILocalService('__APIPROXY__')
    res = service.fieldStatus(obj, method, field)
    return res

  def execMethod(self, obj, method, *args):
    service = APILocalService('__APIPROXY__')
    res = service.execMethod(obj, method, *args)
    return res

  def checkAPIAuth(self, *args):
    service = INTLocalService('__INTAUTHSVC__')
    res = service.checkAPIAuth(*args)
    return res

APIObjectsProxy()

@nativeclass
class MVCObjectsProxy(MVCService):
  def __init__(self, name='__MVC__'):
    super(MVCObjectsProxy, self).__init__(name)
    self.joinGroup('__MVCSVC__')
    self.exportMethod(self.objectList)
    self.exportMethod(self.objectStatus)
    self.exportMethod(self.execMethod)
    self.exportMethod(self.fieldList)
    self.exportMethod(self.getSession)
    self.exportMethod(self.initView)
    self.exportMethod(self.openView)
    self.exportMethod(self.retrieveData)
    self.exportMethod(self.printData)
    self.exportMethod(self.postData)
    self.exportMethod(self.finalizeView)
    self.exportMethod(self.synchronizeData)
    self.exportMethod(self.lookupView)

  def objectList(self):
    service = MVCLocalService('__MVCPROXY__')
    res = service.objectList()
    return res

  def objectStatus(self, obj):
    service = MVCLocalService('__MVCPROXY__')
    res = service.objectStatus(obj)
    return res

  def execMethod(self, obj, method, *args):
    service = MVCLocalService('__MVCPROXY__')
    res = service.execMethod(obj, method, *args)
    return res

  def fieldList(self, obj):
    service = MVCLocalService('__MVCPROXY__')
    res = service.fieldList(obj)
    return res

  def getSession(self, obj):
    service = MVCLocalService('__MVCPROXY__')
    res = service.getSession(obj)
    return res

  def initView(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.initView(obj, *args)

  def openView(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.openView(obj, *args)

  def retrieveData(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.retrieveData(obj, *args)

  def printData(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.printData(obj, *args)

  def postData(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.postData(obj, *args)

  def finalizeView(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.finalizeView(obj, *args)

  def synchronizeData(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.synchronizeData(obj, *args)

  def lookupView(self, obj, *args):
    service = MVCLocalService('__MVCPROXY__')
    return service.lookupView(obj, *args)


MVCObjectsProxy()

@nativeclass
class JOBObjectsProxy(JOBService):
  def __init__(self, name='__JOB__'):
    super(JOBObjectsProxy, self).__init__(name)
    self.joinGroup('__JOBSVC__')
    self.exportMethod(self.getSession)
    self.exportMethod(self.executeJob)

  def getSession(self, *args):
    service = JOBLocalService('__JOBPROXY__')
    res = service.getSession(*args)
    return res

  def executeJob(self, *args):
    service = JOBLocalService('__JOBPROXY__')
    res = service.executeJob(*args)
    return res

JOBObjectsProxy()

@nativeclass
class BusinessObjectsProxy(BusinessObjectService):
  def __init__(self, name='__BOBJ__'):
    super(BusinessObjectsProxy, self).__init__(name)
    self.joinGroup('__BOBJSVC__')
    self.exportMethod(self.getObject)

  def getObject(self, *args):
    service = BusinessObjectLocalService('__BOBJPROXY__')
    res = service.getObject(*args)
    return res

BusinessObjectsProxy()