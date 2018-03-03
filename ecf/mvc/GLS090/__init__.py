"""
Accounting Rules, this module purposed for maintain Account Rules reference which will
be needed by various accounting related modules on this system.
"""

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import ACTRLS, GLACCT, EFUSRS

class GLS090(MVCController):
  """
  Accounting Rules, this module purposed for maintain Account Rules reference which will
  be needed by various accounting related modules on this system.
  """

  _description = 'Accounting Rules'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(ACTRLS)

  ACRLCONO    = MVCField(MVCTypeList + MVCTypeField, String(3), label='Company', visible=False, enabled=False)
  ACRLIDNO    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Rule ID', charcase=ecUpperCase, browseable=True)
  ACRLIDNM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Rule Name', synchronized=True, enabled=False)
  ACRLACID    = MVCField(MVCTypeField, String(48), label='Acct. ID', visible=False, enabled=False)
  ACRLACFM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Acct. Fmt', synchronized=True, browseable=True)
  ACRLACNM    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Acct. Name', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'ACRLACFM':
      ret.svcname = 'GLS450'
      ret.retfield = 'GLACACFM'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''
    fields = mvcsession.entryDataset.FieldsAsDict()
    if fieldName == 'ACRLACFM':
      fldNameAC = fieldName[:6] + 'ID'
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
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    if cono is None:
      cono = ''
    objs = ACTRLS.getObj(True, GLACCONO = cono)
    mvcsession.listDataset.CopyFromORMList(
      'ACRLIDNO;ACRLIDNM;ACRLACFM;ACRLACNM',
      'ACRLIDNO;ACRLIDNM;ACRLACFM;ACRLACNM',
      objs)
    return mvcsession

  def initializeData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    fields = mvcsession.listDataset.FieldsAsDict()
    if cono is None:
      cono = ''

    if mvcsession.execType == MVCExecAppend:
      mvcsession.entryDataset.Append()
      mvcsession.entryDataset.SetFieldValue('ACRLCONO', cono)
      mvcsession.entryDataset.Post()
    return mvcsession


