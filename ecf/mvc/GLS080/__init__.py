"""
G/L Revaluation code, this module purposed for maintain specific specific
reference needed for currency exchange revaluation.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
from validators import *
import datetime as dt
import sqlalchemy as sa
import re
from tbl import GLRVAL, GLACCT, GLSRCE, MSTXRT, EFUSRS


class GLS080(MVCController):
  """
  G/L Revaluation code, this module purposed for maintain specific specific
  reference needed for currency exchange revaluation.
  """

  _description = 'G/L Revaluation Code'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLRVRVNM  = MVCField(MVCTypeList + MVCTypeField, String(6), label='Reval. Code', charcase=ecUpperCase)
  GLRVDESC  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Desc')
  GLRVRTTP  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Rate Type', browseable=True)
  GLRVSRLG  = MVCField(MVCTypeList + MVCTypeField, String(5), label='Source Code', browseable=True)
  GLRVGCFM  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Unrealized Gain', browseable=True, synchronized=True)
  GLRVGCNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Acct. Name', enabled=False)
  GLRVLCFM  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Unrealized Loss.', browseable=True, synchronized=True)
  GLRVLCNM  = MVCField(MVCTypeList + MVCTypeField, String(32), label='Acct. Name.', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'GLRVGCFM':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    if fieldName == 'GLRVLCFM':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    if fieldName == 'GLRVRTTP':
      ret.svcname = 'CMN050'
      ret.retfield = 'CMRTTPCD'
    if fieldName == 'GLRVSRLG':
      ret.svcname = 'GLS040'
      ret.retfield = 'GLSRCEID'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fieldName == 'GLRVGCFM':
      if (fields['GLRVGCFM'] in (None, '')):
        raise Exception('Account ID must not empty')
      acct = GLACCT.stripedacct(fields['GLRVGCFM'])
      q = GLACCT.query.filter_by(GLACCONO = cono)
      obj = q.filter_by(GLACACID = acct).first()
      if not obj:
        raise Exception('Account ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLRVGCFM', obj.GLACACFM)
      mvcsession.entryDataset.SetFieldValue('GLRVGCNM', obj.GLACACNM)
      mvcsession.entryDataset.Post()

    if fieldName == 'GLRVLCFM':
      if (fields['GLRVLCFM'] in (None, '')):
        raise Exception('Account ID must not empty')
      acct = GLACCT.stripedacct(fields['GLRVLCFM'])
      q = GLACCT.query.filter_by(GLACCONO = cono)
      obj = q.filter_by(GLACACID = acct).first()
      if not obj:
        raise Exception('Account ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLRVLCFM', obj.GLACACFM)
      mvcsession.entryDataset.SetFieldValue('GLRVLCNM', obj.GLACACNM)
      mvcsession.entryDataset.Post()

    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''
    objs = GLRVAL.getObj(True, GLRVCONO = cono)
    for obj in objs:
      srlg = None
      if (obj.GLRVSRCE not in (None, '')):
        srlg = "%s-%s" % (obj.GLRVSRCE[:2], obj.GLRVSRCE[2:])
      mvcsession.listDataset.Append()
      mvcsession.listDataset.SetFieldValue('GLRVRVNM', obj.GLRVRVNM)
      mvcsession.listDataset.SetFieldValue('GLRVDESC', obj.GLRVDESC)
      mvcsession.listDataset.SetFieldValue('GLRVRTTP', obj.GLRVRTTP)
      mvcsession.listDataset.SetFieldValue('GLRVSRLG', srlg)
      mvcsession.listDataset.SetFieldValue('GLRVGCFM', obj.GLRVGCFM)
      mvcsession.listDataset.SetFieldValue('GLRVGCNM', obj.GLRVGCNM)
      mvcsession.listDataset.SetFieldValue('GLRVLCFM', obj.GLRVLCFM)
      mvcsession.listDataset.SetFieldValue('GLRVLCNM', obj.GLRVLCNM)
      mvcsession.listDataset.Post()
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      obj = GLRVAL.getObj(False, GLRVCONO = cono, GLRVRVNM = fields['GLRVRVNM'])
      if not obj:
        raise Exception('Could not find selected object')

      srlg = None
      if (obj.GLRVSRCE not in (None, '')):
        srlg = "%s-%s" % (obj.GLRVSRCE[:2], obj.GLRVSRCE[2:])

      mvcsession.entryDataset.Append()
      if (mvcsession.execType == MVCExecCopy):
        mvcsession.entryDataset.SetFieldValue('GLRVRVNM', None)
      else:
        mvcsession.entryDataset.SetFieldValue('GLRVRVNM', obj.GLRVRVNM)
      mvcsession.entryDataset.SetFieldValue('GLRVDESC', obj.GLRVDESC)
      mvcsession.entryDataset.SetFieldValue('GLRVRTTP', obj.GLRVRTTP)
      mvcsession.entryDataset.SetFieldValue('GLRVSRLG', srlg)
      mvcsession.entryDataset.SetFieldValue('GLRVGCFM', obj.GLRVGCFM)
      mvcsession.entryDataset.SetFieldValue('GLRVGCNM', obj.GLRVGCNM)
      mvcsession.entryDataset.SetFieldValue('GLRVLCFM', obj.GLRVLCFM)
      mvcsession.entryDataset.SetFieldValue('GLRVLCNM', obj.GLRVLCNM)
      mvcsession.entryDataset.Post()

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLRVRVNM.enabled = False
    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()

    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''

    obj = GLRVAL.get((cono, fields['GLRVRVNM']))
    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      validators.NotEmpty(messages={'empty': 'Revaluation code must not empty'}).to_python(fields['GLRVRVNM'])

      validators.NotEmpty(messages={'empty': 'Rate type must not empty'}).to_python(fields['GLRVRTTP'])
      mxrt = MSTXRT.get(fields['GLRVRTTP'])
      if not mxrt:
        raise Exception('Rate type code is not found')

      validators.NotEmpty(messages={'empty': 'Source ledger must not empty'}).to_python(fields['GLRVSRLG'])
      splitted = GLSRCE.expandSourceCode(fields['GLRVSRLG'])
      print splitted[2]
      srce = GLSRCE.getObj(False, GLSRCEID = splitted[2])
      if not srce:
        raise Exception('G/L Source code is not found')

      pre = re.compile('\w+')
      validators.NotEmpty(messages={'empty': 'Gain Exchange account must not empty'}).to_python(fields['GLRVGCFM'])
      gacct = GLACCT.get((cono, ''.join(pre.findall(fields['GLRVGCFM']))))
      if not gacct:
        raise Exception('Gain Exchange account is not found')
      if gacct.GLACACST == 0:
        raise Exception('Gain Exchange account is disabled')

      validators.NotEmpty(messages={'empty': 'Loss Exchange account must not empty'}).to_python(fields['GLRVLCFM'])
      lacct = GLACCT.get((cono, ''.join(pre.findall(fields['GLRVLCFM']))))
      if not lacct:
        raise Exception('Loss Exchange account is not found')
      if lacct.GLACACST == 0:
        raise Exception('Loss Exchange account is disabled')

      obj = GLRVAL()
      obj.GLRVCONO    = cono
      obj.GLRVRVNM    = fields['GLRVRVNM']
      obj.GLRVDESC    = fields['GLRVDESC']
      obj.GLRVRTTP    = mxrt.CMRTTPCD
      obj.GLRVSRCE    = splitted[2]
      obj.GLRVSRLG    = splitted[0]
      obj.GLRVSRTP    = splitted[1]
      obj.GLRVGCID    = gacct.GLACACID
      obj.GLRVGCFM    = gacct.GLACACFM
      obj.GLRVGCNM    = gacct.GLACACNM
      obj.GLRVLCID    = lacct.GLACACID
      obj.GLRVLCFM    = lacct.GLACACFM
      obj.GLRVLCNM    = lacct.GLACACNM
      obj.GLRVAUDT    = td.date().tointeger()
      obj.GLRVAUTM    = td.time().tointeger()
      obj.GLRVAUUS    = mvcsession.cookies['user_name'].encode('utf8')

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

      validators.NotEmpty(messages={'empty': 'Rate type must not empty'}).to_python(fields['GLRVRTTP'])
      mxrt = MSTXRT.get(fields['GLRVRTTP'])
      if not mxrt:
        raise Exception('Rate type code is not found')

      validators.NotEmpty(messages={'empty': 'Source ledger must not empty'}).to_python(fields['GLRVSRLG'])
      splitted = GLSRCE.expandSourceCode(fields['GLRVSRLG'])
      srce = GLSRCE.getObj(False, GLSRCEID = splitted[2])
      if not srce:
        raise Exception('G/L Source code is not found')

      pre = re.compile('\w+')
      validators.NotEmpty(messages={'empty': 'Gain Exchange account must not empty'}).to_python(fields['GLRVGCFM'])
      gacct = GLACCT.get((cono, ''.join(pre.findall(fields['GLRVGCFM']))))
      if not gacct:
        raise Exception('Gain Exchange account is not found')
      if gacct.GLACACST == 0:
        raise Exception('Gain Exchange account is disabled')

      validators.NotEmpty(messages={'empty': 'Loss Exchange account must not empty'}).to_python(fields['GLRVLCFM'])
      lacct = GLACCT.get((cono, ''.join(pre.findall(fields['GLRVLCFM']))))
      if not lacct:
        raise Exception('Loss Exchange account is not found')
      if lacct.GLACACST == 0:
        raise Exception('Loss Exchange account is disabled')

      obj.GLRVDESC    = fields['GLRVDESC']
      obj.GLRVRTTP    = mxrt.CMRTTPCD
      obj.GLRVSRCE    = splitted[2]
      obj.GLRVSRLG    = splitted[0]
      obj.GLRVSRTP    = splitted[1]
      obj.GLRVGCID    = gacct.GLACACID
      obj.GLRVGCFM    = gacct.GLACACFM
      obj.GLRVGCNM    = gacct.GLACACNM
      obj.GLRVLCID    = lacct.GLACACID
      obj.GLRVLCFM    = lacct.GLACACFM
      obj.GLRVLCNM    = lacct.GLACACNM
      obj.GLRVAUDT    = td.date().tointeger()
      obj.GLRVAUTM    = td.time().tointeger()
      obj.GLRVAUUS    = mvcsession.cookies['user_name'].encode('utf8')

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

