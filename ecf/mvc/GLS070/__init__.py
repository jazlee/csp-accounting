"""
G/L Batch Numbering Management
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLBCNO

class GLS070(MVCController):
  """
  G/L Batch Numbering Management
  """
  _description = 'G/L Batch Numbering Management'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLBCNOID  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Batch Code', charcase=ecUpperCase)
  GLBCNONM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Description')
  GLBCMINO  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Start From')
  GLBCMXNO  = MVCField(MVCTypeList + MVCTypeField, Integer(), label='Max. No. Accepted')
  GLBCLSNO  = MVCField(MVCTypeList + MVCTypeField, String(6), label='Last No. Used', enabled=False)

  def openView(self, mvcsession):
    q = GLBCNO.query
    q = q.order_by(sa.asc(GLBCNO.GLBCNOID))
    objs = q.all()

    for obj in objs:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('GLBCNOID', obj.GLBCNOID)
      mvcsession.listDataset.SetFieldValue('GLBCNONM', obj.GLBCNONM)
      mvcsession.listDataset.SetFieldValue('GLBCMINO', obj.GLBCMINO)
      mvcsession.listDataset.SetFieldValue('GLBCMXNO', obj.GLBCMXNO)
      mvcsession.listDataset.SetFieldValue('GLBCLSNO', '%.6d' % obj.GLBCLSNO)
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLBCMINO', 0)
      mvcsession.entryDataset.SetFieldValue('GLBCMXNO', 999999)
      mvcsession.entryDataset.SetFieldValue('GLBCLSNO', '%.6d' % 0)
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = GLBCNO.query
      q = q.filter_by(GLBCNOID = fields['GLBCNOID'])
      obj = q.first()

      if (mvcsession.execType == MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLBCNONM;GLBCMINO;GLBCMXNO',
          'GLBCNONM;GLBCMINO;GLBCMXNO',
          obj)
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLBCLSNO', '%.6d' % obj.GLBCLSNO)
        mvcsession.entryDataset.Post()

      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLBCNOID;GLBCNONM;GLBCMINO;GLBCMXNO',
          'GLBCNOID;GLBCNONM;GLBCMINO;GLBCMXNO',
          obj)
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLBCLSNO', '%.6d' % obj.GLBCLSNO)
        mvcsession.entryDataset.Post()

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLBCNOID.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Batch code must not empty'}).to_python(fields['GLBCNOID'])
    validators.NotEmpty(messages={'empty': 'Batch code name must not empty'}).to_python(fields['GLBCNONM'])
    if (fields['GLBCMINO'] is None) or (fields['GLBCMINO'] < 0):
      raise Exception('Minimum batch no must not empty or negative value, at least should be assign with 0')
    if (fields['GLBCMXNO'] is None) or (fields['GLBCMXNO'] > 999999):
      raise Exception('Minimum batch no must not empty or larger than 999999')

    q = GLBCNO.query
    q = q.filter_by(GLBCNOID = fields['GLBCNOID'])
    obj = q.first()

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')

      rec = GLBCNO(
        GLBCNOID = fields['GLBCNOID'],
        GLBCNONM = fields['GLBCNONM'],
        GLBCMINO = fields['GLBCMINO'],
        GLBCMXNO = fields['GLBCMXNO'],
        GLBCLSNO = fields['GLBCMINO'],
        GLBCAUDT = td.date().tointeger(),
        GLBCAUTM = td.time().tointeger(),
        GLBCAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    if (mvcsession.execType == MVCExecEdit):
      if not obj:
        raise Exception('Record could not be found')
      if fields['GLBCMINO'] > obj.GLBCLSNO:
        raise Exception('Starting Batch No must be smaller or equal with last batch no used')
      if fields['GLBCMXNO'] < obj.GLBCLSNO:
        raise Exception('Starting Batch No must be greater or equal with last batch no used')
      mvcsession.entryDataset.CopyIntoORM(
        'GLBCNONM;GLBCMINO;GLBCMXNO',
        'GLBCNONM;GLBCMINO;GLBCMXNO',
        obj)
      obj.GLBCAUDT = td.date().tointeger()
      obj.GLBCAUTM = td.time().tointeger()
      obj.GLBCAUUS = mvcsession.cookies['user_name'].encode('utf8')
      if not session.transaction_started():
        session.begin()
      try:
        session.update(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise

    if (mvcsession.execType == MVCExecDelete):
      if not obj:
        raise Exception('Record could not be found')
      if not session.transaction_started():
        session.begin()
      try:
        session.delete(obj)
        session.commit()
      except:
        session.rollback()
        raise
    return mvcsession



