"""
G/L Source Profile
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import GLPRJN, GLPRIT

class GLS050(MVCController):
  """
  G/L Source Profile
  """

  _description = 'G/L Source Profiles'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLPRPRID  = MVCField(MVCTypeList + MVCTypeField, String(5), label='Code', charcase=ecUpperCase)
  GLPRPRNM  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Profile Name')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'GLS051', params = {'GLITPRID':'%f:GLPRPRID','GLITPRNM':'%f:GLPRPRNM'}, autoSelect=True)
    mvcsession.extFunctions = ( MVCExtFunction('G/L Source Profile Items', 'GLS051', params = {'GLITPRID':'%f:GLPRPRID','GLITPRNM':'%f:GLPRPRNM'}), )
    return mvcsession

  def openView(self, mvcsession):
    q = GLPRJN.query
    q = q.order_by(sa.asc(GLPRJN.GLPRPRID))
    obj = q.all()

    mvcsession.listDataset.CopyFromORMList(
      'GLPRPRID;GLPRPRNM',
      'GLPRPRID;GLPRPRNM',
      obj
      )
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = GLPRJN.query
      q = q.filter_by(GLPRPRID = fields['GLPRPRID'])
      obj = q.first()

      if (mvcsession.execType == MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLPRJNNM',
          'GLPRJNNM',
          obj)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLPRPRID;GLPRPRNM',
          'GLPRPRID;GLPRPRNM',
          obj)

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLPRPRID.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Profile code must not empty'}).to_python(fields['GLPRPRID'])
    validators.NotEmpty(messages={'empty': 'Profile name must not empty'}).to_python(fields['GLPRPRNM'])
    q = GLPRJN.query
    q = q.filter_by(GLPRPRID = fields['GLPRPRID'])
    obj = q.first()

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      rec = GLPRJN(
        GLPRPRID = fields['GLPRPRID'],
        GLPRPRNM = fields['GLPRPRNM'],
        GLPRAUDT = td.date().tointeger(),
        GLPRAUTM = td.time().tointeger(),
        GLPRAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
        'GLPRPRNM',
        'GLPRPRNM',
        obj)
      obj.GLPRAUDT = td.date().tointeger()
      obj.GLPRAUTM = td.time().tointeger()
      obj.GLPRAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      dobjs = GLPRIT.query.filter_by(GLITPRID = fields['GLPRPRID']).all()
      if not session.transaction_started():
        session.begin()
      try:
        for dobj in dobjs:
          session.delete(dobj)
        session.delete(obj)
        session.commit()
      except:
        session.rollback()
        raise
    return mvcsession

