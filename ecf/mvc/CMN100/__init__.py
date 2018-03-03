"""
Company Identification, this module purposed for maintain company ID reference
which will be needed by various modules
on this system.
"""
__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2008 Jaimy Azle'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import MSTCMP

class CMN100(MVCController):
  """
  Company Identification, this module purposed for maintain company ID reference
  which will be needed by various modules
  on this system.
  """

  _description = 'Company Identification'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow)
  _model_binder = MVCModelBinder(MSTCMP)

  CMCPCONO  = MVCField(MVCTypeList + MVCTypeField, String(3), label='Comp. Code', charcase=ecUpperCase)
  CMCPCONM  = MVCField(MVCTypeList + MVCTypeField, String(24), label='Name', synchronized=True)
  CMCPCODS  = MVCField(MVCTypeList + MVCTypeField, String(48), label='Description')
  CMCPADR1  = MVCField(MVCTypeField, String(48), label='Address')
  CMCPADR2  = MVCField(MVCTypeField, String(48), label='Addr #2')
  CMCPADR3  = MVCField(MVCTypeField, String(48), label='Addr #3')
  CMCPZIPC  = MVCField(MVCTypeField, String(48), label='ZIP')
  CMCPARID  = MVCField(MVCTypeField, String(3), label='City', charcase=ecUpperCase, synchronized=True, browseable=True)
  CMCPARNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='City', enabled=False)
  CMCPSTID  = MVCField(MVCTypeField, String(6), label='State', charcase=ecUpperCase, synchronized=True, browseable=True)
  CMCPSTNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='State', enabled=False)
  CMCPCTID  = MVCField(MVCTypeField, String(2), label='Country', charcase=ecUpperCase, synchronized=True, browseable=True)
  CMCPCTNM  = MVCField(MVCTypeList + MVCTypeField, String(16), label='Country', enabled=False)
  CMCPPHN1  = MVCField(MVCTypeField, String(24), label='Phone #1')
  CMCPPHN2  = MVCField(MVCTypeField, String(24), label='Phone #2')
  CMCPFAX1  = MVCField(MVCTypeField, String(24), label='Fax #1')
  CMCPFAX2  = MVCField(MVCTypeField, String(24), label='Fax #2')
  CMCPXEML  = MVCField(MVCTypeField, String(32), label='E-mail')
  CMCPWURL  = MVCField(MVCTypeField, String(48), label='Website')
  CMCPMCST  = MVCField(MVCTypeField, Integer(), label='Multi Currency')
  CMCPCUCD  = MVCField(MVCTypeField, String(3), label='Functional Currency', charcase=ecUpperCase, synchronized=True, browseable=True)
  CMCPCUNM  = MVCField(MVCTypeField, String(16), label='Currency Name', enabled=False)
  CMCPRTCD  = MVCField(MVCTypeField, String(3), label='Default Rate Type', charcase=ecUpperCase, synchronized=True, browseable=True)
  CMCPRTNM  = MVCField(MVCTypeField, String(16), label='Rate Name', enabled=False)

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = ( MVCExtFunction('Company Connect Division', 'CMN110',
        params = {
          'CMDVCONO':'%f:CMCPCONO'
        }),
      MVCExtFunction('Facilities', 'CMN120'),
      )

    return mvcsession


  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'CMCPCONM') and \
       (fields['CMCPCONM'] != '') and \
       (fields['CMCPCODS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPCODS', fields['CMCPCONM'])
      mvcsession.entryDataset.Post()
    if (fieldName == 'CMCPARID'):
      usrobj = proxy.getObject('USROBJ')
      cmnobj = proxy.getObject('CMNOBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      arinfo = cmnobj.getArea( usrinfo['USRCONO'], fields['CMCPARID'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPARID', arinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMCPARNM', arinfo[1])
      mvcsession.entryDataset.Post()
    if (fields['CMCPSTID'] not in (None, '')):
      usrobj = proxy.getObject('USROBJ')
      cmnobj = proxy.getObject('CMNOBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      stinfo = cmnobj.getState( usrinfo['USRCONO'], fields['CMCPSTID'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPSTID', stinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMCPSTNM', stinfo[1])
      mvcsession.entryDataset.Post()
    if (fields['CMCPCTID'] not in (None, '')):
      cmnobj = proxy.getObject('CMNOBJ')
      ctrinfo = cmnobj.getCountry( fields['CMCPCTID'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPCTID', ctrinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMCPCTNM', ctrinfo[1])
      mvcsession.entryDataset.Post()
    if (fields['CMCPCUCD'] not in (None, '')):
      curobj = proxy.getObject('CUROBJ')
      curinfo = curobj.getCurrency( fields['CMCPCUCD'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPCUCD', curinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMCPCUNM', curinfo[1])
      mvcsession.entryDataset.Post()
    if (fields['CMCPRTCD'] not in (None, '')):
      curobj = proxy.getObject('CUROBJ')
      curinfo = curobj.getRateType(fields['CMCPRTCD'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMCPRTCD', curinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMCPRTNM', curinfo[1])
      mvcsession.entryDataset.Post()
    return mvcsession

  def lookupView(self, mvcsession, fieldName):
    ret = MVCLookupDef('','')
    if fieldName == 'CMCPARID':
      ret.svcname = 'CMN030'
      ret.retfield = 'CMARIDCD'
    if fieldName == 'CMCPSTID':
      ret.svcname = 'CMN020'
      ret.params = {'CMPRCTCD':'%f:CMCPCTID'}
      ret.retfield = 'CMSTIDCD'
    if fieldName == 'CMCPCTID':
      ret.svcname = 'CMN010'
      ret.retfield = 'CMCTIDCD'
    if fieldName == 'CMCPCTID':
      ret.svcname = 'CMN010'
      ret.retfield = 'CMCTIDCD'
    if fieldName == 'CMCPCUCD':
      ret.svcname = 'CMN040'
      ret.retfield = 'CMCRCUCD'
    if fieldName == 'CMCPRTCD':
      ret.svcname = 'CMN050'
      ret.retfield = 'CMRTTPCD'
    return ret

  def checkUserCONO(self, mvcsession):
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
    if usrinfo['USRCONO'] is None:
      mvcsession.fieldDefs.CMCPSTID.enabled = False
      mvcsession.fieldDefs.CMCPARID.enabled = False

  def afterRetrieveData(self, mvcsession, obj):
    '''Event triggered after retrieving data'''
    if mvcsession.execType == MVCExecEdit:
      mvcsession.fieldDefs.CMCPCONO.enabled = False
      mvcsession.fieldDefs.CMCPCUCD.enabled = False
    if mvcsession.execType != MVCExecDelete:
      self.checkUserCONO(mvcsession)
    return (mvcsession, obj)

  def initializeData(self, mvcsession):
    '''Initializing data'''
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMCPMCST', 1)
    mvcsession.entryDataset.Post()
    self.checkUserCONO(mvcsession)
    return mvcsession

  def validateData(self, mvcsession):
    '''Validate date retrieved from user input before storing it into persistent storage'''
    if mvcsession.execType in (MVCExecEdit, MVCExecAppend):
      fields = mvcsession.entryDataset.FieldsAsDict()
      proxy = self.getBusinessObjectProxy()
      validators.NotEmpty(messages={'empty': 'Functional currency code must not empty'}).to_python(fields['CMCPCUCD'])
      validators.NotEmpty(messages={'empty': 'Default rate type must not empty'}).to_python(fields['CMCPRTCD'])

      curobj = proxy.getObject('CUROBJ')
      curinfo = curobj.getRateType(fields['CMCPRTCD'])
      validators.NotEmpty(messages={'empty': 'Default rate type must not empty'}).to_python(curinfo[0])
    return mvcsession

  def afterPostData(self, mvcsession, obj):
    '''Event triggered after posting data'''
    proxy = self.getBusinessObjectProxy()
    cmpobj = proxy.getObject('CMPOBJ')
    if mvcsession.execType == MVCExecEdit:
      cmpobj.updateCOMPCache(obj)
    elif mvcsession.execType == MVCExecDelete:
      cmpobj.removeCOMPCache(obj)
    return (mvcsession, obj)



