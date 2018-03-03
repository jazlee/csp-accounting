"""
G/L Source Code
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
from tbl import GLSRCE

class GLS040(MVCController):
  """
  G/L Source Code
  """

  _description = 'G/L Source Code'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLSRCEID  = MVCField(MVCTypeList + MVCTypeField, String(5), label='Source Code', charcase=ecUpperCase)
  GLSRCENM  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Name')

  def openView(self, mvcsession):
    q = GLSRCE.query
    q = q.order_by(sa.asc(GLSRCE.GLSRCEID))
    objs = q.all()

    for obj in objs:
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('GLSRCEID', "%s-%s" % (obj.GLSRCEID[:2], obj.GLSRCEID[2:]))
      mvcsession.listDataset.SetFieldValue('GLSRCENM', obj.GLSRCENM)
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLSRCEID', 'SR-CD')
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      proxy = self.getBusinessObjectProxy()
      glsobj = proxy.getObject('GLSOBJ')
      splitted = glsobj.expandGLSourceCode(fields['GLSRCEID'])
      q = GLSRCE.query
      q = q.filter_by(GLSRCEID = splitted[2])
      obj = q.first()

      if (mvcsession.execType == MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLSRCENM',
          'GLSRCENM',
          obj)
      else:
        mvcsession.entryDataset.Append()
        mvcsession.entryDataset.SetFieldValue('GLSRCEID', "%s-%s" % (obj.GLSRCEID[:2], obj.GLSRCEID[2:]))
        mvcsession.entryDataset.SetFieldValue('GLSRCENM', obj.GLSRCENM)
        mvcsession.entryDataset.Post()

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLSRCEID.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Source code must not empty'}).to_python(fields['GLSRCEID'])
    proxy = self.getBusinessObjectProxy()
    glsobj = proxy.getObject('GLSOBJ')
    splitted = glsobj.expandGLSourceCode(fields['GLSRCEID'])
    q = GLSRCE.query
    q = q.filter_by(GLSRCEID = splitted[2])
    obj = q.first()

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      rec = GLSRCE(
        GLSRCEID = splitted[2],
        GLSRCESR = splitted[0],
        GLSRCETP = splitted[1],
        GLSRCENM = fields['GLSRCENM'],
        GLSRAUDT = td.date().tointeger(),
        GLSRAUTM = td.time().tointeger(),
        GLSRAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
        'GLSRCENM',
        'GLSRCENM',
        obj)
      obj.GLSRAUDT = td.date().tointeger()
      obj.GLSRAUTM = td.time().tointeger()
      obj.GLSRAUUS = mvcsession.cookies['user_name'].encode('utf8')
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

