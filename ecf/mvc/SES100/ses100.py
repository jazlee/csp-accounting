"""
MVC User Accessibility
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
import datetime as dt
import sqlalchemy as sa
from elixir import *
from validators import *
from tbl import EFUMOB

class SES100(MVCController):
  """
  MVC User Accessibility
  """

  _description = 'MVC User Accessibility'
  _active = True
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  UMOUSRNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(24), label = 'User Name', browseable=True, charcase=ecUpperCase)
  UMOOBJNM = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(32), label = 'MVC Service', browseable=True, charcase=ecUpperCase)
  UMOOBJDS = MVCField(MVCTypeList, String(48), label = 'Description')
  UMOOBJSL = MVCField(MVCTypeField, Integer(), label = 'Select')
  UMOOBJIN = MVCField(MVCTypeField, Integer(), label = 'Insert')
  UMOOBJUP = MVCField(MVCTypeField, Integer(), label = 'Update')
  UMOOBJDL = MVCField(MVCTypeField, Integer(), label = 'Delete')
  UMOOBJEX = MVCField(MVCTypeField, Integer(), label = 'Execute')

  def initView(self, mvcsession):
    return mvcsession

  def openView(self, mvcsession):
    if mvcsession.paramDataset.RecordCount == 0:
      mvcsession.paramDataset.Append()
      mvcsession.paramDataset.SetFieldValue('UMOUSRNM', mvcsession.cookies['user_name'].encode('utf8'))
      mvcsession.paramDataset.Post()
    mvcsvc = MVCLocalService('__MVCPROXY__')
    params = mvcsession.paramDataset.FieldsAsDict()
    q = EFUMOB.query
    if (params['UMOUSRNM'] not in (None, '')):
      q = q.filter_by(UMOUSRNM = params['UMOUSRNM'])
    if (params['UMOOBJNM'] not in (None, '')):
      q = q.filter_by(UMOOBJNM = params['UMOOBJNM'])
    objs = q.order_by(sa.asc(EFUMOB.UMOUSRNM)).all()
    for obj in objs:
      mvcsession.listDataset.CopyFromORM(
        'UMOUSRNM;UMOOBJNM',
        'UMOUSRNM;UMOOBJNM',
        obj)
      if (obj.UMOOBJNM != '*') and (obj.UMOOBJNM != ' '):
        try:
          objInfo = mvcsvc.objectStatus(obj.UMOOBJNM)
          if objInfo[1]:
            mvcsession.listDataset.Edit()
            mvcsession.listDataset.SetFieldValue('UMOOBJDS', objInfo[1])
            mvcsession.listDataset.Post()
        except:
          mvcsession.listDataset.Edit()
          mvcsession.listDataset.SetFieldValue('UMOOBJDS', 'Unknown Object')
          mvcsession.listDataset.Post()

    return mvcsession

  def retrieveData(self, mvcsession):
    lists = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType == MVCExecAppend:
      # Setup default value
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('UMOOBJSL', 0)
      mvcsession.entryDataset.SetFieldValue('UMOOBJIN', 0)
      mvcsession.entryDataset.SetFieldValue('UMOOBJUP', 0)
      mvcsession.entryDataset.SetFieldValue('UMOOBJDL', 0)
      mvcsession.entryDataset.SetFieldValue('UMOOBJEX', 0)
      mvcsession.entryDataset.Post()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = EFUMOB.query
      q = q.filter_by(UMOUSRNM = lists['UMOUSRNM'])
      q = q.filter_by(UMOOBJNM = lists['UMOOBJNM'])
      objs = q.order_by(sa.asc(EFUMOB.UMOUSRNM)).first()

      if mvcsession.execType != MVCExecCopy:
        mvcsession.entryDataset.CopyFromORM(
          'UMOUSRNM;UMOOBJNM;UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
          'UMOUSRNM;UMOOBJNM;UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
        objs)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'UMOOBJNM;UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
          'UMOOBJNM;UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
          objs)
      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.UMOUSRNM.enabled = False
        mvcsession.fieldDefs.UMOOBJNM.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    entries = mvcsession.entryDataset.FieldsAsDict()
    now = dt.datetime.now()
    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      q = EFUMOB.query
      q = q.filter_by(UMOUSRNM = entries['UMOUSRNM'])
      q = q.filter_by(UMOOBJNM = entries['UMOOBJNM'])
      obj = q.first()
      if obj:
        raise Exception('existing record is found in the database')
      if (entries['UMOOBJNM'] == ' '):
        raise Exception('object name is not a valid name')
      obj = EFUMOB(
        UMOUSRNM = entries['UMOUSRNM'],
        UMOOBJNM = entries['UMOOBJNM'],
        UMOOBJSL = entries['UMOOBJSL'],
        UMOOBJIN = entries['UMOOBJIN'],
        UMOOBJUP = entries['UMOOBJUP'],
        UMOOBJDL = entries['UMOOBJDL'],
        UMOOBJEX = entries['UMOOBJEX'],
        UMOOAUDT = now.date().tointeger(),
        UMOOAUTM = now.time().tointeger(),
        UMOOAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      q = EFUMOB.query
      q = q.filter_by(UMOUSRNM = entries['UMOUSRNM'])
      q = q.filter_by(UMOOBJNM = entries['UMOOBJNM'])
      obj = q.first()
      if not obj:
        raise Exception('The record could not be found in the database')
      mvcsession.entryDataset.CopyIntoORM(
        'UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
        'UMOOBJSL;UMOOBJIN;UMOOBJUP;UMOOBJDL;UMOOBJEX',
        obj)
      obj.UMOOAUDT = now.date().tointeger()
      obj.UMOOAUTM = now.time().tointeger()
      obj.UMOOAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      q = EFUMOB.query
      q = q.filter_by(UMOUSRNM = entries['UMOUSRNM'])
      q = q.filter_by(UMOOBJNM = entries['UMOOBJNM'])
      obj = q.first()
      if not obj:
        raise Exception('record could not be found in the database')
      if not session.transaction_started():
        session.begin()
      session.delete(obj)
      session.commit()
    return mvcsession

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'UMOUSRNM':
      ret.svcname = 'SES010'
      ret.retfield = 'EFUSUSID'
      ret.params = {'EFUSUSTP':''}
    if fieldName == 'UMOOBJNM':
      ret.svcname = 'SES020'
      ret.retfield = 'EFMVCONM'
    return ret

  def finalizeView(self, mvcsession):
    return mvcsession

