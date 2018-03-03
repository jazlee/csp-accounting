"""
Account Set, this module purposed for maintain Account set reference
which will be needed by various modules on this system.
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
from tbl import GLACCT, EFUSRS, GLSOPT, GLACST

class GLS460(MVCController):
  """
  Account Set, this module purposed for maintain Account set reference
  which will be needed by various modules on this system.
  """
  _description = 'Account Sets'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)

  GLACSTNM    = MVCField(MVCTypeList + MVCTypeField, String(6), label='Acct. Set')
  GLACSTDS    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')
  GLACACST    = MVCField(MVCTypeList + MVCTypeField, Integer, label='Active')
  GLARCUCD    = MVCField(MVCTypeField, String(3), label='A/R Currency', browseable=True)
  GLARCTAC    = MVCField(MVCTypeField, String(48), label='A/R Control Acct.', visible=False, enabled=False)
  GLARCTFM    = MVCField(MVCTypeField, String(48), label='A/R Control Acct.', synchronized=True, browseable=True)
  GLARCTNM    = MVCField(MVCTypeField, String(32), label='A/R Control Acct.', enabled=False)
  GLARDCAC    = MVCField(MVCTypeField, String(48), label='A/R Receipt Discount', visible=False, enabled=False)
  GLARDCFM    = MVCField(MVCTypeField, String(48), label='A/R Receipt Discount', synchronized=True, browseable=True)
  GLARDCNM    = MVCField(MVCTypeField, String(32), label='A/R Receipt Discount', enabled=False)
  GLARPPAC    = MVCField(MVCTypeField, String(48), label='A/R Prepayment Liability', visible=False, enabled=False)
  GLARPPFM    = MVCField(MVCTypeField, String(48), label='A/R Prepayment Liability', synchronized=True, browseable=True)
  GLARPPNM    = MVCField(MVCTypeField, String(32), label='A/R Prepayment Liability', enabled=False)
  GLARWOAC    = MVCField(MVCTypeField, String(48), label='A/R Write-Offs', visible=False, enabled=False)
  GLARWOFM    = MVCField(MVCTypeField, String(48), label='A/R Write-Offs', synchronized=True, browseable=True)
  GLARWONM    = MVCField(MVCTypeField, String(32), label='A/R Write-Offs', enabled=False)
  GLARGXAC    = MVCField(MVCTypeField, String(48), label='A/R Unrealized Exch. Gain', visible=False, enabled=False)
  GLARGXFM    = MVCField(MVCTypeField, String(48), label='A/R Unrealized Exch. Gain', synchronized=True, browseable=True)
  GLARGXNM    = MVCField(MVCTypeField, String(32), label='A/R Unrealized Exch. Gain', enabled=False)
  GLARLXAC    = MVCField(MVCTypeField, String(48), label='A/R Unrealized Exch. Loss', visible=False, enabled=False)
  GLARLXFM    = MVCField(MVCTypeField, String(48), label='A/R Unrealized Exch. Loss', synchronized=True, browseable=True)
  GLARLXNM    = MVCField(MVCTypeField, String(32), label='A/R Unrealized Exch. Loss', enabled=False)
  GLARGRAC    = MVCField(MVCTypeField, String(48), label='A/R Realized Exch. Gain', visible=False, enabled=False)
  GLARGRFM    = MVCField(MVCTypeField, String(48), label='A/R Realized Exch. Gain', synchronized=True, browseable=True)
  GLARGRNM    = MVCField(MVCTypeField, String(32), label='A/R Realized Exch. Gain', enabled=False)
  GLARLRAC    = MVCField(MVCTypeField, String(48), label='A/R Realized Exch. Loss', visible=False, enabled=False)
  GLARLRFM    = MVCField(MVCTypeField, String(48), label='A/R Realized Exch. Loss', synchronized=True, browseable=True)
  GLARLRNM    = MVCField(MVCTypeField, String(32), label='A/R Realized Exch. Loss', enabled=False)
  GLAPCUCD    = MVCField(MVCTypeField, String(3), label='A/P Currency', browseable=True)
  GLAPCTAC    = MVCField(MVCTypeField, String(48), label='A/P Control Acct.', visible=False, enabled=False)
  GLAPCTFM    = MVCField(MVCTypeField, String(48), label='A/P Control Acct.', synchronized=True, browseable=True)
  GLAPCTNM    = MVCField(MVCTypeField, String(32), label='A/P Control Acct.', enabled=False)
  GLAPDCAC    = MVCField(MVCTypeField, String(48), label='A/P Payment Discount', visible=False, enabled=False)
  GLAPDCFM    = MVCField(MVCTypeField, String(48), label='A/P Payment Discount', synchronized=True, browseable=True)
  GLAPDCNM    = MVCField(MVCTypeField, String(32), label='A/P Payment Discount', enabled=False)
  GLAPPPAC    = MVCField(MVCTypeField, String(48), label='A/P Prepayment', visible=False, enabled=False)
  GLAPPPFM    = MVCField(MVCTypeField, String(48), label='A/P Prepayment', synchronized=True, browseable=True)
  GLAPPPNM    = MVCField(MVCTypeField, String(32), label='A/P Prepayment', enabled=False)
  GLAPGXAC    = MVCField(MVCTypeField, String(48), label='A/P Unrealized Exch. Gain', visible=False, enabled=False)
  GLAPGXFM    = MVCField(MVCTypeField, String(48), label='A/P Unrealized Exch. Gain', synchronized=True, browseable=True)
  GLAPGXNM    = MVCField(MVCTypeField, String(32), label='A/P Unrealized Exch. Gain', enabled=False)
  GLAPLXAC    = MVCField(MVCTypeField, String(48), label='A/P Unrealized Exch. Loss', visible=False, enabled=False)
  GLAPLXFM    = MVCField(MVCTypeField, String(48), label='A/P Unrealized Exch. Loss', synchronized=True, browseable=True)
  GLAPLXNM    = MVCField(MVCTypeField, String(32), label='A/P Unrealized Exch. Loss', enabled=False)
  GLAPGRAC    = MVCField(MVCTypeField, String(48), label='A/P Realized Exch. Gain', visible=False, enabled=False)
  GLAPGRFM    = MVCField(MVCTypeField, String(48), label='A/P Realized Exch. Gain', synchronized=True, browseable=True)
  GLAPGRNM    = MVCField(MVCTypeField, String(32), label='A/P Realized Exch. Gain', enabled=False)
  GLAPLRAC    = MVCField(MVCTypeField, String(48), label='A/P Realized Exch. Loss', visible=False, enabled=False)
  GLAPLRFM    = MVCField(MVCTypeField, String(48), label='A/P Realized Exch. Loss', synchronized=True, browseable=True)
  GLAPLRNM    = MVCField(MVCTypeField, String(32), label='A/P Realized Exch. Loss', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName not in ('GLARCUCD', 'GLAPCUCD'):
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    else:
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if cono is None:
      cono = ''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fieldName not in ('GLARCUCD', 'GLAPCUCD'):
      fldNameAC = fieldName[:6] + 'AC'
      fldNameFM = fieldName[:6] + 'FM'
      fldNameNM = fieldName[:6] + 'NM'
      if (fields[fldNameFM] in (None, '')):
        raise Exception('Account ID must not empty')
      acct = GLACCT.stripedacct(fields[fldNameFM])
      obj = GLACCT.get((cono, acct))
      if not obj:
        raise Exception('Account ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue(fldNameAC, obj.GLACACID)
      mvcsession.entryDataset.SetFieldValue(fldNameFM, obj.GLACACFM)
      mvcsession.entryDataset.SetFieldValue(fldNameNM, obj.GLACACNM)
      mvcsession.entryDataset.Post()

    return mvcsession

  def openView(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if cono is None:
      cono = ''
    objs = GLACST.getObj(True, GLACCONO = cono)
    mvcsession.listDataset.CopyFromORMList('GLACSTNM;GLACSTDS;GLACACST','GLACSTNM;GLACSTDS;GLACACST',objs)
    return mvcsession

  def retrieveData(self, mvcsession):
    fields = mvcsession.listDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if cono is None:
      cono = ''

    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('GLACACST', 1)
      mvcsession.entryDataset.Post()

    if mvcsession.execType in (MVCExecShow, MVCExecEdit, MVCExecDelete, MVCExecCopy):
      obj = GLACST.getObj(False, GLACCONO = cono, GLACSTNM = fields['GLACSTNM'])
      if not obj:
        raise Exception('Could not find selected object')

      srlg = None
      if mvcsession.execType == MVCExecCopy:
        fldList = \
          'GLACSTDS;GLACACST;GLARCUCD;GLARCTAC;GLARCTFM;GLARCTNM;' \
          'GLARDCAC;GLARDCFM;GLARDCNM;GLARPPAC;GLARPPFM;GLARPPNM;GLARWOAC;' \
          'GLARWOFM;GLARWONM;GLARGXAC;GLARGXFM;GLARGXNM;GLARLXAC;GLARLXFM;' \
          'GLARLXNM;GLARGRAC;GLARGRFM;GLARGRNM;GLARLRAC;GLARLRFM;GLARLRNM;' \
          'GLAPCUCD;GLAPCTAC;GLAPCTFM;GLAPCTNM;GLAPDCAC;GLAPDCFM;GLAPDCNM;' \
          'GLAPPPAC;GLAPPPFM;GLAPPPNM;GLAPGXAC;GLAPGXFM;GLAPGXNM;GLAPLXAC;' \
          'GLAPLXFM;GLAPLXNM;GLAPGRAC;GLAPGRFM;GLAPGRNM;GLAPLRAC;GLAPLRFM;' \
          'GLAPLRNM'
      else:
        fldList = \
          'GLACSTNM;GLACSTDS;GLACACST;GLARCUCD;GLARCTAC;GLARCTFM;GLARCTNM;' \
          'GLARDCAC;GLARDCFM;GLARDCNM;GLARPPAC;GLARPPFM;GLARPPNM;GLARWOAC;' \
          'GLARWOFM;GLARWONM;GLARGXAC;GLARGXFM;GLARGXNM;GLARLXAC;GLARLXFM;' \
          'GLARLXNM;GLARGRAC;GLARGRFM;GLARGRNM;GLARLRAC;GLARLRFM;GLARLRNM;' \
          'GLAPCUCD;GLAPCTAC;GLAPCTFM;GLAPCTNM;GLAPDCAC;GLAPDCFM;GLAPDCNM;' \
          'GLAPPPAC;GLAPPPFM;GLAPPPNM;GLAPGXAC;GLAPGXFM;GLAPGXNM;GLAPLXAC;' \
          'GLAPLXFM;GLAPLXNM;GLAPGRAC;GLAPGRFM;GLAPGRNM;GLAPLRAC;GLAPLRFM;' \
          'GLAPLRNM'

      mvcsession.entryDataset.CopyFromORM(fldList, fldList, obj)

      if mvcsession.execType == MVCExecEdit:
        mvcsession.fieldDefs.GLACSTNM.enabled = False

    return mvcsession

  def postData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if cono is None:
      cono = ''

    obj = GLACST.get((cono, fields['GLACSTNM']))
    td = dt.datetime.now()
    if (mvcsession.execType in (MVCExecAppend, MVCExecCopy)):
      if obj:
        raise Exception('Duplicate record found')
      validators.NotEmpty(messages={'empty': 'Acct set Name must not empty'}).to_python(fields['GLACSTNM'])
      fldList = \
        'GLACSTNM;GLACSTDS;GLACACST;GLARCUCD;GLARCTAC;GLARCTFM;GLARCTNM;' \
        'GLARDCAC;GLARDCFM;GLARDCNM;GLARPPAC;GLARPPFM;GLARPPNM;GLARWOAC;' \
        'GLARWOFM;GLARWONM;GLARGXAC;GLARGXFM;GLARGXNM;GLARLXAC;GLARLXFM;' \
        'GLARLXNM;GLARGRAC;GLARGRFM;GLARGRNM;GLARLRAC;GLARLRFM;GLARLRNM;' \
        'GLAPCUCD;GLAPCTAC;GLAPCTFM;GLAPCTNM;GLAPDCAC;GLAPDCFM;GLAPDCNM;' \
        'GLAPPPAC;GLAPPPFM;GLAPPPNM;GLAPGXAC;GLAPGXFM;GLAPGXNM;GLAPLXAC;' \
        'GLAPLXFM;GLAPLXNM;GLAPGRAC;GLAPGRFM;GLAPGRNM;GLAPLRAC;GLAPLRFM;' \
        'GLAPLRNM'
      obj = GLACST()
      mvcsession.entryDataset.CopyIntoORM(fldList, fldList, obj)
      obj.GLACCONO    = cono
      obj.GLACAUDT    = td.date().tointeger()
      obj.GLACAUTM    = td.time().tointeger()
      obj.GLACAUUS    = mvcsession.cookies['user_name'].encode('utf8')
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
      fldList = \
        'GLACSTDS;GLACACST;GLARCUCD;GLARCTAC;GLARCTFM;GLARCTNM;' \
        'GLARDCAC;GLARDCFM;GLARDCNM;GLARPPAC;GLARPPFM;GLARPPNM;GLARWOAC;' \
        'GLARWOFM;GLARWONM;GLARGXAC;GLARGXFM;GLARGXNM;GLARLXAC;GLARLXFM;' \
        'GLARLXNM;GLARGRAC;GLARGRFM;GLARGRNM;GLARLRAC;GLARLRFM;GLARLRNM;' \
        'GLAPCUCD;GLAPCTAC;GLAPCTFM;GLAPCTNM;GLAPDCAC;GLAPDCFM;GLAPDCNM;' \
        'GLAPPPAC;GLAPPPFM;GLAPPPNM;GLAPGXAC;GLAPGXFM;GLAPGXNM;GLAPLXAC;' \
        'GLAPLXFM;GLAPLXNM;GLAPGRAC;GLAPGRFM;GLAPGRNM;GLAPLRAC;GLAPLRFM;' \
        'GLAPLRNM'
      mvcsession.entryDataset.CopyIntoORM(fldList, fldList, obj)
      obj.GLACAUDT    = td.date().tointeger()
      obj.GLACAUTM    = td.time().tointeger()
      obj.GLACAUUS    = mvcsession.cookies['user_name'].encode('utf8')
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


