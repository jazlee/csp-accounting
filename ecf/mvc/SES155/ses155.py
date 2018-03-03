"""
API Function Accessibility
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
import datetime as dt
import apisvc as api
import sqlalchemy as sa
from elixir import *
from tbl import EFUAFN

class SES155(MVCController):
  """
  API Function User Accessibility
  """
  _description = 'API Functions User Accessibility'
  _active = True
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  UAFUSRNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(24), label = 'User Name', enabled=False, charcase=ecUpperCase)
  UAFOBJNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(32), label = 'API Service', enabled=False, charcase=ecUpperCase)
  UAFFNCNM = MVCField(MVCTypeField + MVCTypeList, String(32), label = 'Function Name', browseable=True, charcase=ecUpperCase)
  UAFFNCDS = MVCField(MVCTypeList, String(48), label = 'Description')
  UAFFNCSL = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Select')
  UAFFNCIN = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Insert')
  UAFFNCUP = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Update')
  UAFFNCDL = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Delete')
  UAFFNCEX = MVCField(MVCTypeField + MVCTypeList, Integer(), label = 'Execute')

  def initView(self, mvcsession):
    return mvcsession

  def openView(self, mvcsession):
    if mvcsession.paramDataset.RecordCount == 0:
      raise Exception('Program SES155 could not be load directly by user')

    params = mvcsession.paramDataset.FieldsAsDict()
    apiservice = api.APILocalService('__APIPROXY__')
    q = EFUAFN.query
    if (params['UAFUSRNM'] not in ('', None)):
      q = q.filter_by(UAFUSRNM = params['UAFUSRNM'])
    if (params['UAFOBJNM'] not in ('', None)):
      q = q.filter_by(UAFOBJNM = params['UAFOBJNM'])
    objs = q.order_by(sa.asc(EFUAFN.UAFUSRNM)).all()
    for obj in objs:
      mvcsession.listDataset.CopyFromORM(
        'UAFUSRNM;UAFOBJNM;UAFFNCNM',
        'UAFUSRNM;UAFOBJNM;UAFFNCNM',
        obj)
      mvcsession.listDataset.Edit()
      if obj.UAFFNCSL:
        mvcsession.listDataset.SetFieldValue('UAFFNCSL', 1)
      else:
        mvcsession.listDataset.SetFieldValue('UAFFNCSL', 0)
      if obj.UAFFNCIN:
        mvcsession.listDataset.SetFieldValue('UAFFNCIN', 1)
      else:
        mvcsession.listDataset.SetFieldValue('UAFFNCIN', 0)
      if obj.UAFFNCUP:
        mvcsession.listDataset.SetFieldValue('UAFFNCUP', 1)
      else:
        mvcsession.listDataset.SetFieldValue('UAFFNCUP', 0)
      if obj.UAFFNCDL:
        mvcsession.listDataset.SetFieldValue('UAFFNCDL', 1)
      else:
        mvcsession.listDataset.SetFieldValue('UAFFNCDL', 0)
      if obj.UAFFNCEX:
        mvcsession.listDataset.SetFieldValue('UAFFNCEX', 1)
      else:
        mvcsession.listDataset.SetFieldValue('UAFFNCEX', 0)
      if obj.UAFFNCNM != '*':
        objInfo = apiservice.methodStatus(obj.UAFOBJNM, obj.UAFFNCNM)
        if objInfo[1]:
          mvcsession.listDataset.SetFieldValue('UAFFNCDS', objInfo[1])
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    if mvcsession.execType == MVCExecAppend:
      params = mvcsession.paramDataset.FieldsAsDict()
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('UAFUSRNM', params['UAFUSRNM'])
      mvcsession.entryDataset.SetFieldValue('UAFOBJNM', params['UAFOBJNM'])
      mvcsession.entryDataset.SetFieldValue('UAFFNCSL', 0)
      mvcsession.entryDataset.SetFieldValue('UAFFNCIN', 0)
      mvcsession.entryDataset.SetFieldValue('UAFFNCUP', 0)
      mvcsession.entryDataset.SetFieldValue('UAFFNCDL', 0)
      mvcsession.entryDataset.SetFieldValue('UAFFNCEX', 0)
      mvcsession.entryDataset.Post()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      fields = mvcsession.listDataset.FieldsAsDict()
      q = EFUAFN.query
      q = q.filter_by(UAFUSRNM = fields['UAFUSRNM'])
      q = q.filter_by(UAFOBJNM = fields['UAFOBJNM'])
      q = q.filter_by(UAFFNCNM = fields['UAFFNCNM'])
      objs = q.order_by(sa.asc(EFUAFN.UAFUSRNM)).first()

      if mvcsession.execType != MVCExecCopy:
        mvcsession.entryDataset.CopyFromORM(
          'UAFUSRNM;UAFOBJNM;UAFFNCNM',
          'UAFUSRNM;UAFOBJNM;UAFFNCNM',
        objs)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'UAFUSRNM;UAFOBJNM',
          'UAFUSRNM;UAFOBJNM',
          objs)
      mvcsession.entryDataset.Edit()
      if objs.UAFFNCSL:
        mvcsession.entryDataset.SetFieldValue('UAFFNCSL', 1)
      else:
        mvcsession.entryDataset.SetFieldValue('UAFFNCSL', 0)
      if objs.UAFFNCIN:
        mvcsession.entryDataset.SetFieldValue('UAFFNCIN', 1)
      else:
        mvcsession.entryDataset.SetFieldValue('UAFFNCIN', 0)
      if objs.UAFFNCUP:
        mvcsession.entryDataset.SetFieldValue('UAFFNCUP', 1)
      else:
        mvcsession.entryDataset.SetFieldValue('UAFFNCUP', 0)
      if objs.UAFFNCDL:
        mvcsession.entryDataset.SetFieldValue('UAFFNCDL', 1)
      else:
        mvcsession.entryDataset.SetFieldValue('UAFFNCDL', 0)
      if objs.UAFFNCEX:
        mvcsession.entryDataset.SetFieldValue('UAFFNCEX', 1)
      else:
        mvcsession.entryDataset.SetFieldValue('UAFFNCEX', 0)
      mvcsession.entryDataset.Post()
      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.UAFUSRNM.enabled = False
        mvcsession.fieldDefs.UAFOBJNM.enabled = False
        mvcsession.fieldDefs.UAFFNCNM.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    now = dt.datetime.now()
    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      q = EFUAFN.query
      q = q.filter_by(UAFUSRNM = fields['UAFUSRNM'])
      q = q.filter_by(UAFOBJNM = fields['UAFOBJNM'])
      q = q.filter_by(UAFFNCNM = fields['UAFFNCNM'])
      obj = q.first()
      if obj:
        raise Exception('existing record is found in the database')
      obj = EFUAFN(
        UAFUSRNM = fields['UAFUSRNM'],
        UAFOBJNM = fields['UAFOBJNM'],
        UAFFNCNM = fields['UAFFNCNM'],
        UAFFNCSL = fields['UAFFNCSL'] == 1,
        UAFFNCIN = fields['UAFFNCIN'] == 1,
        UAFFNCUP = fields['UAFFNCUP'] == 1,
        UAFFNCDL = fields['UAFFNCDL'] == 1,
        UAFFNCEX = fields['UAFFNCEX'] == 1,
        UAFFAUDT = now.date().tointeger(),
        UAFFAUTM = now.time().tointeger(),
        UAFFAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
    if mvcsession.execType == MVCExecEdit:
      q = EFUAFN.query
      q = q.filter_by(UAFUSRNM = fields['UAFUSRNM'])
      q = q.filter_by(UAFOBJNM = fields['UAFOBJNM'])
      q = q.filter_by(UAFFNCNM = fields['UAFFNCNM'])
      obj = q.first()
      if not obj:
        raise Exception('The record could not be found in the database')
      obj.UAFFNCSL = fields['UAFFNCSL'] == 1
      obj.UAFFNCIN = fields['UAFFNCIN'] == 1
      obj.UAFFNCUP = fields['UAFFNCUP'] == 1
      obj.UAFFNCDL = fields['UAFFNCDL'] == 1
      obj.UAFFNCEX = fields['UAFFNCEX'] == 1
      obj.UAFFAUDT = now.date().tointeger()
      obj.UAFFAUTM = now.time().tointeger()
      obj.UAFFAUUS = mvcsession.cookies['user_name'].encode('utf8')
      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    if mvcsession.execType == MVCExecDelete:
      q = EFUAFN.query
      q = q.filter_by(UAFUSRNM = fields['UAFUSRNM'])
      q = q.filter_by(UAFOBJNM = fields['UAFOBJNM'])
      q = q.filter_by(UAFFNCNM = fields['UAFFNCNM'])
      obj = q.first()
      if not obj:
        raise Exception('The record could not be found in the database')
      if not session.transaction_started():
        session.begin()
      session.delete(obj)
      session.commit()
    return mvcsession

  def lookupView(self, mvcsession, fieldName):
    if fieldName == 'UAFFNCNM':
      return MVCLookupDef('SES031','EFAPIFNM', params = {'EFAPIONM':'%f:UAFOBJNM'})
    else:
      return MVCLookupDef('','')

  def finalizeView(self, mvcsession):
    return mvcsession

