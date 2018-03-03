"""
G/L Source Profile Items
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLPRIT, GLPRJN, GLSRCE

class GLS051(MVCController):
  """
  G/L Source Profile Items
  """
  _description = 'G/L Source Profile Items'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncDelete)

  GLITPRID  = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(4), label='Profile Code', charcase=ecUpperCase, enabled=False)
  GLITPRNM  = MVCField(MVCTypeParam, String(48), label='Profile Name', enabled=False)
  GLITCEID  = MVCField(MVCTypeList + MVCTypeField, String(5), label='Source Code', charcase=ecUpperCase, browseable=True, synchronized=True)
  GLITCENM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Source Name', enabled=False)

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fields['GLITCEID'] not in ('', None)):
      splitted = GLSRCE.expandSourceCode(fields['GLITCEID'])
      obj = GLSRCE.query.filter_by(GLSRCEID = splitted[2]).first()
      if obj:
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLITCENM', obj.GLSRCENM)
        mvcsession.entryDataset.Post()
    return mvcsession

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLITCEID':
      ret.svcname = 'GLS040'
      ret.retfield = 'GLSRCEID'
    return ret

  def openView(self, mvcsession):
    fields = mvcsession.paramDataset.FieldsAsDict()
    if mvcsession.paramDataset.RecordCount == 0:
      raise Exception('Program GLS051 could not be load directly by user')

    q = GLPRIT.query
    q = q.filter_by(GLITPRID = fields['GLITPRID'])
    q = q.order_by(sa.asc(GLPRIT.GLITPRID))
    q = q.order_by(sa.asc(GLPRIT.GLITCEID))
    objs = q.all()

    for obj in objs:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('GLITPRID', obj.GLITPRID)
      mvcsession.listDataset.SetFieldValue('GLITCEID', "%s-%s" % (obj.GLITCEID[:2], obj.GLITCEID[2:]))
      mvcsession.listDataset.SetFieldValue('GLITCENM', obj.GLITCENM)
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    params = mvcsession.paramDataset.FieldsAsDict()
    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLITPRID', params['GLITPRID'])
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      splitted = GLPRIT.expandSourceCode(fields['GLITCEID'])
      q = GLPRIT.query
      q = q.filter_by(GLITPRID = fields['GLITPRID'])
      q = q.filter_by(GLITCEID = splitted[2])
      obj = q.first()

      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLITPRID', obj.GLITPRID)
      mvcsession.entryDataset.SetFieldValue('GLITCEID', "%s-%s" % (obj.GLITCEID[:2], obj.GLITCEID[2:]))
      mvcsession.entryDataset.SetFieldValue('GLITCENM', obj.GLITCENM)
      mvcsession.entryDataset.Post()

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLITCEID.enabled = False
        mvcsession.fieldDefs.GLITPRID.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Profile code must not empty'}).to_python(fields['GLITPRID'])
    validators.NotEmpty(messages={'empty': 'Source code must not empty'}).to_python(fields['GLITCEID'])
    splitted = GLPRIT.expandSourceCode(fields['GLITCEID'])
    q = GLPRIT.query
    q = q.filter_by(GLITPRID = fields['GLITPRID'])
    q = q.filter_by(GLITCEID = splitted[2])
    obj = q.first()
    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      rec = GLPRIT(
        GLITPRID = fields['GLITPRID'],
        GLITCEID = splitted[2],
        GLITCESR = splitted[0],
        GLITCETP = splitted[1],
        GLITCENM = fields['GLITCENM'],
        GLITAUDT = td.date().tointeger(),
        GLITAUTM = td.time().tointeger(),
        GLITAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      mvcsession.entryDataset.CopyIntoORM(
        'GLITCENM',
        'GLITCENM',
        obj)
      obj.GLITAUDT = td.date().tointeger()
      obj.GLITAUTM = td.time().tointeger()
      obj.GLITAUUS = mvcsession.cookies['user_name'].encode('utf8')
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

