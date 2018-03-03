"""
G/L Account Currencies
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
from validators import *
import sqlalchemy as sa
import re
from tbl import GLACCT, EFUSRS, GLACRV, MSTCUR, GLRVAL

class GLS452(MVCController):
  """
  G/L Account Currencies
  """
  _description = 'G/L Account Currencies'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLRVACID    = MVCField(MVCTypeParam, String(48), label='Acct ID', visible=False)
  GLRVACFM    = MVCField(MVCTypeParam, String(48), label='Acct ID', enabled=False)
  GLRVACNM    = MVCField(MVCTypeParam, String(48), label='Acct Name', enabled=False)
  GLRVCUCD    = MVCField(MVCTypeList + MVCTypeField, String(3), label='Currency', browseable=True, charcase=ecUpperCase, synchronized=True)
  GLRVCUNM    = MVCField(MVCTypeList + MVCTypeField, String(16), label='Cur. Name', enabled=False)
  GLRVRVST    = MVCField(MVCTypeList + MVCTypeField, Integer, label='Revaluation')
  GLRVRVNM    = MVCField(MVCTypeList + MVCTypeField, String(6), label='Rev. Code', browseable=True, charcase=ecUpperCase, synchronized=True)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLRVCUCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    if fieldName == 'GLRVRVNM':
      ret.svcname = 'GLS080'
      ret.retfield = 'GLRVRVNM'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (fieldName == 'GLRVCUCD'):
      if (fields['GLRVCUCD'] not in (None, '')):
        obj = MSTCUR.query.filter_by(CMCRCUCD = fields['GLRVCUCD']).first()
        if obj:
          mvcsession.entryDataset.Edit()
          mvcsession.entryDataset.SetFieldValue('GLRVCUNM', obj.CMCRCUNM)
          mvcsession.entryDataset.Post()
    if (fieldName == 'GLRVRVNM'):
      if (fields['GLRVRVNM'] not in (None, '')):
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLRVRVST', 1)
        mvcsession.entryDataset.Post()


    return mvcsession

  def openView(self, mvcsession):
    if mvcsession.paramDataset.IsEmpty:
      raise Exception('Program GLS452 could not be load directly by user')

    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))

    acct = GLACCT.get((cono, params['GLRVACID']))
    if acct:
      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('GLRVACFM', acct.GLACACFM)
      mvcsession.paramDataset.SetFieldValue('GLRVACNM', acct.GLACACNM)
      mvcsession.paramDataset.Post()

    q = GLACRV.query
    q = q.filter_by(GLRVCONO = cono)
    q = q.filter_by(GLRVACID = params['GLRVACID'])
    q = q.order_by(sa.asc(GLACRV.GLRVCONO))
    q = q.order_by(sa.asc(GLACRV.GLRVACID))
    q = q.order_by(sa.asc(GLACRV.GLRVCUCD))
    obj = q.all()
    mvcsession.listDataset.CopyFromORMList(
      'GLRVCUCD;GLRVCUNM;GLRVRVST;GLRVRVNM',
      'GLRVCUCD;GLRVCUNM;GLRVRVST;GLRVRVNM',
      obj
      )
    return mvcsession

  def retrieveData(self, mvcsession):
    lists = mvcsession.listDataset.FieldsAsDict()
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))

    if mvcsession.execType in (MVCExecAppend, MVCExecCopy):
      acctid = GLACCT.get((cono, params['GLRVACID']))
      if not acctid:
        raise Exception('Master account is not found')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLRVRVST', 0)
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      obj = GLACRV.get((cono, params['GLRVACID'], lists['GLRVCUCD']))

      if (mvcsession.execType != MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLRVCUCD;GLRVCUNM;GLRVRVST;GLRVRVNM',
          'GLRVCUCD;GLRVCUNM;GLRVRVST;GLRVRVNM',
          obj)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLRVRVST;GLRVRVNM',
          'GLRVRVST;GLRVRVNM',
          obj)

    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.GLRVCUCD.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    params = mvcsession.paramDataset.FieldsAsDict()
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Curr code must not empty'}).to_python(fields['GLRVCUCD'])

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))

    sacct = GLACCT.get((cono, params['GLRVACID']))
    if not sacct:
      raise Exception('Master account does not exist')

    cur = MSTCUR.get((fields['GLRVCUCD']))
    if not cur:
      raise Exception('Currency does not exist')

    rval = None
    if fields['GLRVRVNM'] not in (None, ''):
      obj = GLRVAL.get((cono, fields['GLRVRVNM']))
      if not obj:
        raise Exception('Revaluation code does not exist')
      rval = obj.GLRVRVNM

    obj = GLACRV.get((cono, params['GLRVACID'], fields['GLRVCUCD']))

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      obj = GLACRV()
      obj.GLRVCONO = cono
      obj.GLRVACID = sacct.GLACACID
      obj.GLRVCUCD = cur.CMCRCUCD
      obj.GLRVCUNM = cur.CMCRCUNM
      obj.GLRVRVST = fields['GLRVRVST']
      obj.GLRVRVNM = rval
      obj.GLRVAUDT = td.date().tointeger()
      obj.GLRVAUTM = td.time().tointeger()
      obj.GLRVAUUS = mvcsession.cookies['user_name'].encode('utf8')

      if not session.transaction_started():
        session.begin()
      try:
        session.save(obj)
        session.commit()
      except:
        session.rollback()
        session.expunge(obj)
        raise
    if (mvcsession.execType == MVCExecEdit):
      if not obj:
        raise Exception('Record could not be found')

      obj.GLRVRVST = fields['GLRVRVST']
      obj.GLRVRVNM = rval
      obj.GLRVAUDT = td.date().tointeger()
      obj.GLRVAUTM = td.time().tointeger()
      obj.GLRVAUUS = mvcsession.cookies['user_name'].encode('utf8')

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


