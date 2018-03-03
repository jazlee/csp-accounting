"""
G/L Group Of Account
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
from tbl import GLACGR, GLACCT, EFUSRS, GLSACS, GLSOPT, MSTUOM, GLSRCE, MSTCMP

class GLS455(MVCController):
  """
  G/L Group Of Account
  """
  _description = 'G/L Group Of Account'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(GLACGR)

  GLAGCONO    = MVCField(MVCTypeList + MVCTypeField, String(3), label='Comp. ID', visible=False)
  GLAGACID    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Group ID', visible=False)
  GLAGSTID    = MVCField(MVCTypeField, String(8), label='Default structure', synchronized=True, browseable=True)
  GLAGSTNM    = MVCField(MVCTypeField, String(32),label='structure name', enabled=False)
  GLAGACFM    = MVCField(MVCTypeList + MVCTypeField, String(48), label='Group. ID', synchronized=True)
  GLAGACLV    = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, Integer, label='Level')
  GLAGACSQ    = MVCField(MVCTypeList + MVCTypeField, Integer, label='Sequence level')
  GLAGACNM    = MVCField(MVCTypeList + MVCTypeField, String(32), label='Group Name', synchronized=True)
  GLAGACDS    = MVCField(MVCTypeField, String(48), label='Description')
  GLAGACTP    = MVCField(MVCTypeField, String(1), label='Acct. Type',
                  choices={
                      'Income Statement':'I',
                      'Balance Sheet':'B',
                      'Retained Earnings':'R'
                  })
  GLAGGRTP    = MVCField(MVCTypeField, Integer, label='Acct. group',
                  choices={
                        'Current assets':1,
                        'Fixed assets':2,
                        'Other assets':3,
                        'Accumulated depreciation':4,
                        'Current liabilities':5,
                        'Long term liabilities':6,
                        'Stockholders\' equity':7,
                        'Revenue':8,
                        'Cost of sales':9,
                        'Opening inventory':10,
                        'Purchases':11,
                        'Closing inventory':12,
                        'Cost and expenses':13,
                        'Other income and expenses':14,
                        'Provision for income taxes':15,
                        'Others':17
                  })
  GLAGA1ID    = MVCField(MVCTypeField, String(48), label='Grp Level 1', visible=False)
  GLAGA1FM    = MVCField(MVCTypeField, String(48), label='Grp Level 1', charcase=ecUpperCase, synchronized=True, browseable=True)
  GLAGA1NM    = MVCField(MVCTypeField, String(32), label='Grp Level 1', enabled=False)
  GLAGA2ID    = MVCField(MVCTypeField, String(48), label='Grp Level 2', visible=False)
  GLAGA2FM    = MVCField(MVCTypeField, String(48), label='Grp Level 2', charcase=ecUpperCase, synchronized=True, browseable=True)
  GLAGA2NM    = MVCField(MVCTypeField, String(32), label='Grp Level 2', enabled=False)
  GLAGA3ID    = MVCField(MVCTypeField, String(48), label='Grp Level 3', visible=False)
  GLAGA3FM    = MVCField(MVCTypeField, String(48), label='Grp Level 3', charcase=ecUpperCase, synchronized=True, browseable=True)
  GLAGA3NM    = MVCField(MVCTypeField, String(32), label='Grp Level 3', enabled=False)
  GLAGA4ID    = MVCField(MVCTypeField, String(48), label='Grp Level 4', visible=False)
  GLAGA4FM    = MVCField(MVCTypeField, String(48), label='Grp Level 4', charcase=ecUpperCase, synchronized=True, browseable=True)
  GLAGA4NM    = MVCField(MVCTypeField, String(32), label='Grp Level 4', enabled=False)

  def lookupView(self, session, fieldName):
    ret = MVCLookupDef('','')
    if fieldName in ('GLAGA1FM', 'GLAGA2FM', 'GLAGA3FM', 'GLAGA4FM'):
      ret.svcname = 'GLS455'
      ret.params = {'GLAGACLV': '%%v:%s' % fieldName[5]}
      ret.retfield = 'GLAGACFM'
    if fieldName == 'GLAGSTID':
      ret.svcname = 'GLS030'
      ret.retfield = 'ACASACCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if fieldName not in ('GLAGSTID', 'GLAGACFM', 'GLAGACNM'):
      fldNameAC = fieldName[:6] + 'ID'
      fldNameFM = fieldName[:6] + 'FM'
      fldNameNM = fieldName[:6] + 'NM'
      if (fields[fldNameFM] in (None, '')):
        raise Exception('Group ID must not empty')
      acct = GLACGR.stripedacct(fields[fldNameFM])
      obj = GLACGR.get((cono, acct))
      if not obj:
        raise Exception('Group ID does not exist')

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue(fldNameAC, obj.GLAGACID)
      mvcsession.entryDataset.SetFieldValue(fldNameFM, obj.GLAGACFM)
      mvcsession.entryDataset.SetFieldValue(fldNameNM, obj.GLAGACNM)
      mvcsession.entryDataset.Post()
    elif (fieldName == 'GLAGSTID') and \
       (fields['GLAGSTID'] not in (None, '')):
      obj = GLSACS.query.filter_by(ACASACCD = fields['GLAGSTID']).first()
      if not obj:
        raise Exception('Account structure %s is not valid' % fields['GLAGSTID'])

      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLAGSTNM', obj.ACASACNM)
      mvcsession.entryDataset.Post()

    elif ((fieldName == 'GLAGSTID') or (fieldName == 'GLAGACFM')) and \
       (fields['GLAGACFM'] not in (None, '')) and \
       (fields['GLAGSTID'] not in (None, '')) and \
       (cono != None):

      fmtvalue = GLACGR.formatacct(cono, fields['GLAGSTID'], fields['GLAGACFM'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('GLAGACFM', fmtvalue[0])
      mvcsession.entryDataset.SetFieldValue('GLAGACID', GLACGR.stripedacct(fmtvalue[0]))
      mvcsession.entryDataset.Post()
    elif (fieldName == 'GLAGACNM'):
      if (fields['GLAGACNM'] != None) and \
         (fields['GLAGACDS'] in ('', None)):
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('GLAGACDS', fields['GLAGACNM'])
        mvcsession.entryDataset.Post()

    return mvcsession

  def initializeParam(self, mvcsession, query):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user %s is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    params = mvcsession.paramDataset.FieldsAsDict()
    query = query.filter_by(GLAGCONO = cono)
    if params['GLAGACLV'] != None:
      query = query.filter_by(GLAGACLV = params['GLAGACLV'])
    return query

  def initializeData(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user %s is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    opt = GLSOPT.get(cono)
    mstcmp = MSTCMP.get(cono)
    if not mstcmp:
      raise Exception('Default company has not been setup')
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('GLAGCONO', cono)
    mvcsession.entryDataset.SetFieldValue('GLAGSTID', opt.GLOPACSC)
    mvcsession.entryDataset.SetFieldValue('GLAGACTP', 'I')
    mvcsession.entryDataset.SetFieldValue('GLAGGRTP', 1)
    mvcsession.entryDataset.SetFieldValue('GLAGACLV', 5)
    mvcsession.entryDataset.SetFieldValue('GLAGACSQ', 5)
    if (opt.GLOPACSC not in (None, '')):
      obj = GLSACS.get(opt.GLOPACSC)
      if not obj:
        raise Exception('Account structure %s is not found' % fields['GLAGSTID'])
      mvcsession.entryDataset.SetFieldValue('GLAGSTNM', obj.ACASACNM)
    mvcsession.entryDataset.Post()
    return mvcsession

  def validateData(self, mvcsession):
    fields = mvcsession.entryDataset.FieldsAsDict()
    validators.NotEmpty(messages={'empty': 'Acct code must not empty'}).to_python(fields['GLAGACFM'])
    validators.NotEmpty(messages={'empty': 'Default acct structure must not empty'}).to_python(fields['GLAGSTID'])
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    glsobj = proxy.getObject('GLSOBJ')
    info = usrobj.retrieveUserInfoDict(mvcsession)
    cono = info['USRCONO']
    glopt = glsobj.getGLOpt(cono)
    if (cono in (None, '')):
      raise Exception('Default company for user % is not assigned' % mvcsession.cookies['user_name'].encode('utf8'))
    return mvcsession

