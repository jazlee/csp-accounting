"""
API User Accessibility
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
import apisvc as api
import datetime as dt
import sqlalchemy as sa
from elixir import *
from tbl import EFUAOB

class SES150(MVCController):
  """
  API User Accessibility
  """

  _description = 'API User Accessibility'
  _active = True
  _supported_functions = (MVCFuncNew, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  UAOUSRNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(24), label = 'User Name', browseable=True, charcase=ecUpperCase)
  UAOOBJNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(32), label = 'API Service', browseable=True, charcase=ecUpperCase, synchronized=True)
  UAOOBJDS = MVCField(MVCTypeField + MVCTypeList, String(48), label = 'Description', enabled=False)

  def initView(self, mvcsession):
    mvcsession.extFunctions = (
      MVCExtFunction('Open API Functions access list', 'SES155', params = {'UAFUSRNM':'%f:UAOUSRNM', 'UAFOBJNM':'%f:UAOOBJNM'}),
      )
    mvcsession.selectFunction = MVCExtFunction('Open API Functions access list', 'SES155', params = {'UAFUSRNM':'%f:UAOUSRNM', 'UAFOBJNM':'%f:UAOOBJNM'})
    return mvcsession

  def openView(self, mvcsession):
    if mvcsession.paramDataset.RecordCount == 0:
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('UAOUSRNM', mvcsession.cookies['user_name'].encode('utf8'))
      mvcsession.paramDataset.Post()
    params = mvcsession.paramDataset.FieldsAsDict()
    apiservice = api.APILocalService('__APIPROXY__')
    q = EFUAOB.query
    if (params['UAOUSRNM'] not in (None, '')):
      q = q.filter_by(UAOUSRNM = params['UAOUSRNM'])
    if (params['UAOOBJNM'] not in (None, '')):
      q = q.filter_by(UAOOBJNM = params['UAOOBJNM'])
    objs = q.order_by(sa.asc(EFUAOB.UAOUSRNM)).all()
    for obj in objs:
      mvcsession.listDataset.CopyFromORM(
        'UAOUSRNM;UAOOBJNM',
        'UAOUSRNM;UAOOBJNM',
        obj)
      if obj.UAOOBJNM != '*':
        objInfo = apiservice.objectStatus(obj.UAOOBJNM)
        if objInfo[1]:
          mvcsession.listDataset.Edit()
          mvcsession.listDataset.SetFieldValue('UAOOBJDS', objInfo[1])
          mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    apiservice = api.APILocalService('__APIPROXY__')
    if mvcsession.execType == MVCExecAppend:
      if mvcsession.paramDataset.GetFieldValue('UAOUSRNM') not in (None, ''):
        mvcsession.entryDataset.Append()
        mvcsession.entryDataset.SetFieldValue('UAOUSRNM', mvcsession.paramDataset.GetFieldValue('UAOUSRNM'))
        mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = EFUAOB.query
      q = q.filter_by(UAOUSRNM = mvcsession.listDataset.GetFieldValue('UAOUSRNM'))
      q = q.filter_by(UAOOBJNM = mvcsession.listDataset.GetFieldValue('UAOOBJNM'))
      objs = q.order_by(sa.asc(EFUAOB.UAOUSRNM)).first()

      if mvcsession.execType != MVCExecCopy:
        mvcsession.entryDataset.CopyFromORM(
          'UAOUSRNM;UAOOBJNM',
          'UAOUSRNM;UAOOBJNM',
        objs)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'UAOOBJNM',
          'UAOOBJNM',
          objs)
      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.UAOUSRNM.enabled = False
        mvcsession.fieldDefs.UAOOBJNM.enabled = False
      if objs.UAOOBJNM != '*':
        objInfo = apiservice.objectStatus(objs.UAOOBJNM)
        if objInfo[1]:
          mvcsession.entryDataset.Edit()
          mvcsession.entryDataset.SetFieldValue('UAOOBJDS', objInfo[1])
          mvcsession.entryDataset.Post()

    return mvcsession

  def postData(self, mvcsession):
    entries = mvcsession.entryDataset.FieldsAsDict()
    now = dt.datetime.now()
    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      q = EFUAOB.query
      q = q.filter_by(UAOUSRNM = entries['UAOUSRNM'])
      q = q.filter_by(UAOOBJNM = entries['UAOOBJNM'])
      obj = q.first()
      if obj:
        raise Exception('existing record is found in the database')
      obj = EFUAOB(
        UAOUSRNM = entries['UAOUSRNM'],
        UAOOBJNM = entries['UAOOBJNM'],
        UAUUAUDT = now.date().tointeger(),
        UAOOAUTM = now.time().tointeger(),
        UAOOAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    if mvcsession.execType == MVCExecShow:
      pass
    if mvcsession.execType == MVCExecDelete:
      q = EFUAOB.query
      q = q.filter_by(UAOUSRNM = entries['UAOUSRNM'])
      q = q.filter_by(UAOOBJNM = entries['UAOOBJNM'])
      obj = q.first()
      if not obj:
        raise Exception('record could not be found in the database')
      if not session.transaction_started():
        session.begin()
      try:
        session.delete(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    return mvcsession

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'UAOUSRNM':
      ret.svcname = 'SES010'
      ret.params = {'EFUSUSTP':''}
      ret.retfield = 'EFUSUSID'
    if fieldName == 'UAOOBJNM':
      ret.svcname = 'SES030'
      ret.retfield = 'EFAPIONM'
    return ret

  def finalizeView(self, mvcsession):
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    apiservice = api.APILocalService('__APIPROXY__')
    entries = mvcsession.entryDataset.FieldsAsDict()
    mvcsession.entryDataset.Edit()
    if (entries['UAOOBJNM'] not in (None, '*', '')):
      objInfo = apiservice.objectStatus(entries['UAOOBJNM'])
      if objInfo[1]:
        mvcsession.entryDataset.SetFieldValue('UAOOBJDS', objInfo[1])
    mvcsession.entryDataset.Post()
    return mvcsession

