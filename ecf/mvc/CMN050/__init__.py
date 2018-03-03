"""
Exchange Rate, this module purposed for maintain exchange rate reference linked
from currency module which will be needed by various modules on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import MSTXRT

class CMN050(MVCController):
  """
  Exchange Rate, this module purposed for maintain exchange rate reference linked
  from currency module which will be needed by various modules on this system.
  """

  _description = 'Exchange Rate Types'
  _supported_functions = (MVCFuncSelect, MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  CMRTTPCD  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Rate Type', charcase=ecUpperCase)
  CMRTTPNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Name', synchronized=True)
  CMRTTPDS  = MVCField(MVCTypeField, String(32), label='Description')

  def initView(self, mvcsession):
    mvcsession.selectFunction = MVCExtFunction('xxx', 'CMN045', params = {'CMCTTPCD':'%f:CMRTTPCD'}, autoSelect=False)
    mvcsession.extFunctions = ( MVCExtFunction('Currency rate type', 'CMN045', params = {'CMCTTPCD':'%f:CMRTTPCD'}),
      MVCExtFunction('Currencies', 'CMN040'))
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    if (fields['CMRTTPNM'] not in (None, '')) and \
       (fields['CMRTTPDS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMRTTPDS', fields['CMRTTPNM'])
      mvcsession.entryDataset.Post()
    return mvcsession

  def openView(self, mvcsession):
    obj = MSTXRT.query.order_by(sa.asc(MSTXRT.CMRTTPCD)).all()

    mvcsession.listDataset.CopyFromORMList(
      'CMRTTPCD;CMRTTPNM',
      'CMRTTPCD;CMRTTPNM',
      obj
      )
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = MSTXRT.query
      q = q.filter_by(CMRTTPCD = fields['CMRTTPCD'])
      obj = q.first()

      if (mvcsession.execType == MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'CMRTTPNM;CMRTTPDS',
          'CMRTTPNM;CMRTTPDS',
          obj)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'CMRTTPCD;CMRTTPNM;CMRTTPDS',
          'CMRTTPCD;CMRTTPNM;CMRTTPDS',
          obj)

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.CMRTTPCD.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    q = MSTXRT.query
    q = q.filter_by(CMRTTPCD = fields['CMRTTPCD'])
    obj = q.first()
    today = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      validators.NotEmpty(messages={'empty': 'Rate type code must not empty'}).to_python(fields['CMRTTPCD'])
      validators.NotEmpty(messages={'empty': 'Rate type name must not empty'}).to_python(fields['CMRTTPNM'])
      rec = MSTXRT(
        CMRTTPCD = fields['CMRTTPCD'],
        CMRTTPNM = fields['CMRTTPNM'],
        CMRTTPDS = fields['CMRTTPDS'],
        CMRTAUDT = today.date().tointeger(),
        CMRTAUTM = today.time().tointeger(),
        CMRTAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
        'CMRTTPNM;CMRTTPDS',
        'CMRTTPNM;CMRTTPDS',
        obj)
      obj.CMRTAUDT = today.date().tointeger()
      obj.CMRTAUTM = today.time().tointeger()
      obj.CMRTAUUS = mvcsession.cookies['user_name'].encode('utf8')
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
      session.delete(obj)
      session.commit()
    return mvcsession


