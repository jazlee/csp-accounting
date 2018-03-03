"""
G/L Allocation Account Items
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import decimal as dcm
from ecfutil import CurrencyContext
from validators import *
import sqlalchemy as sa
import re
from tbl import GLACCT, EFUSRS, GLALAC


class GLS451(MVCController):
  """
  G/L Allocation Account Items
  """

  _description = 'G/L Allocation Account Items'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLALACID    = MVCField(MVCTypeParam, String(48), label='Acct ID', visible=False)
  GLALACFM    = MVCField(MVCTypeParam, String(48), label='Acct ID', enabled=False)
  GLALACNM    = MVCField(MVCTypeParam, String(48), label='Acct Name', enabled=False)
  GLACALPC    = MVCField(MVCTypeParam, Numeric(7,4), label='Total Percentage', enabled=False)
  GLALALID    = MVCField(MVCTypeList, String(48), label='AcctID', visible=False)
  GLALALFM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Acct ID', browseable=True, synchronized=True)
  GLALALNM    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Acct. Name', enabled=False)
  GLALALRF    = MVCField(MVCTypeField, String(48), label='Reference')
  GLALALPC    = MVCField(MVCTypeList + MVCTypeField, Numeric(7,4), label='Percentage')

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLALALFM':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (fieldName == 'GLALALFM'):
      if (fields['GLALALFM'] in (None, '')):
        raise Exception('Account ID must not empty')

      acct = glsobj.stripedacct(fields['GLALALFM'])
      q = GLACCT.query.filter_by(GLACCONO = cono)
      obj = q.filter_by(GLACACID = acct).first()
      if not obj:
        raise Exception('Account ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLALALFM', obj.GLACACFM)
      mvcsession.entryDataset.SetFieldValue('GLALALNM', obj.GLACACNM)
      mvcsession.entryDataset.Post()

    return mvcsession

  def openView(self, mvcsession):
    if mvcsession.paramDataset.IsEmpty:
      raise Exception('Program GLS451 could not be load directly by user')

    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))

    acct = GLACCT.get((cono, params['GLALACID']))
    if acct:
      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValue('GLACALPC', acct.GLACALPC)
      mvcsession.paramDataset.SetFieldValue('GLALACFM', acct.GLACACFM)
      mvcsession.paramDataset.SetFieldValue('GLALACNM', acct.GLACACNM)
      mvcsession.paramDataset.Post()

    q = GLALAC.query
    q = q.filter_by(GLALCONO = cono)
    q = q.filter_by(GLALACID = params['GLALACID'])
    obj = q.all()
    mvcsession.listDataset.CopyFromORMList(
      'GLALALID;GLALALFM;GLALALNM;GLALALPC',
      'GLALALID;GLALALFM;GLALALNM;GLALALPC',
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
      acctid = GLACCT.get((cono, params['GLALACID']))
      if not acctid:
        raise Exception('Master account is not found')
      if acctid.GLACALST != 1:
        raise Exception('Master account is not marked to use allocation')

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      q = GLALAC.query
      q = q.filter_by(GLALCONO = cono)
      q = q.filter_by(GLALACID = params['GLALACID'])
      q = q.filter_by(GLALALID = lists['GLALALID'])
      obj = q.first()

      if (mvcsession.execType != MVCExecCopy):
        mvcsession.entryDataset.CopyFromORM(
          'GLALALFM;GLALALNM;GLALALRF;GLALALPC',
          'GLALALFM;GLALALNM;GLALALRF;GLALALPC',
          obj)
      else:
        mvcsession.entryDataset.CopyFromORM(
          'GLALALRF;GLALALPC',
          'GLALALRF;GLALALPC',
          obj)

    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.GLALALFM.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    params = mvcsession.paramDataset.FieldsAsDict()
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Acct code must not empty'}).to_python(fields['GLALALFM'])
    validators.NotEmpty(messages={'empty': 'Allocation percentage must not empty'}).to_python(fields['GLALALPC'])
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    pre = re.compile('\w+')
    acct = ''.join(pre.findall(fields['GLALALFM']))
    if acct == params['GLALACID']:
      raise Exception('Account used to be allocated could not be reused with allocation detail')

    sacct = GLACCT.get((cono, params['GLALACID']))
    if not sacct:
      raise Exception('Master account does not exist')

    ret = GLACCT.get((cono, acct))
    if not ret:
      raise Exception('Account does not exist')
    fmtvalue = ret.GLACACFM

    q = GLALAC.query
    q = q.filter_by(GLALCONO = cono)
    q = q.filter_by(GLALACID = params['GLALACID'])
    q = q.filter_by(GLALALID = acct)
    obj = q.first()

    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      rec = GLALAC(
        GLALCONO = cono,
        GLALACID = sacct.GLACACID,
        GLALALID = ret.GLACACID,
        GLALALFM = ret.GLACACFM,
        GLALALNM = ret.GLACACNM,
        GLALALRF = fields['GLALALRF'],
        GLALALPC = fields['GLALALPC'],
        GLALAUDT = td.date().tointeger(),
        GLALAUTM = td.time().tointeger(),
        GLALAUUS = mvcsession.cookies['user_name'].encode('utf8')
      )
      dcm.getcontext().prec = 9
      sacct.GLACALPC  = dcm.Decimal(sacct.GLACALPC + dcm.Decimal(rec.GLALALPC, CurrencyContext), CurrencyContext)
      if not session.transaction_started():
        session.begin()
      try:
        session.save(rec)
        session.update(sacct)
        session.commit()
      except:
        session.rollback()
        session.expunge(rec)
        raise
    if (mvcsession.execType == MVCExecEdit):
      if not obj:
        raise Exception('Record could not be found')
      dcm.getcontext().prec = 9
      sacct.GLACALPC  = dcm.Decimal(sacct.GLACALPC - dcm.Decimal(obj.GLALALPC, CurrencyContext), CurrencyContext)
      mvcsession.entryDataset.CopyIntoORM(
        'GLALALRF;GLALALPC',
        'GLALALRF;GLALALPC',
        obj)
      obj.GLALAUDT = td.date().tointeger()
      obj.GLALAUTM = td.time().tointeger()
      obj.GLALAUUS = mvcsession.cookies['user_name'].encode('utf8')
      if not session.transaction_started():
        session.begin()
      try:
        dcm.getcontext().prec = 9
        sacct.GLACALPC  = dcm.Decimal(sacct.GLACALPC + dcm.Decimal(obj.GLALALPC, CurrencyContext), CurrencyContext)
        session.update(obj)
        session.update(sacct)
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
        dcm.getcontext().prec = 9
        sacct.GLACALPC  = dcm.Decimal(sacct.GLACALPC - dcm.Decimal(obj.GLALALPC, CurrencyContext), CurrencyContext)
        session.delete(obj)
        session.update(sacct)
        session.commit()
      except:
        session.rollback()
        raise

    return mvcsession