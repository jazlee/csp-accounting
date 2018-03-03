#
# Copyright (c) 2009 Cipta Solusi Pratama. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 Cipta Solusi Pratama'

from mvcsvc import *
from elixir import *
import datetime as dt
import sqlalchemy as sa
from validators import *
from tbl import CMPDIV, MSTCMP, MSTARE

class CMN110(MVCController):
  """
  Company connect division
  """

  _description = 'Company connect division'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(CMPDIV)

  CMDVCONO  = MVCField(MVCTypeField+MVCTypeList+MVCTypeParam, String(3), label='Company', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDVCONM  = MVCField(MVCTypeField, String(24), label='Company Name', enabled=False)
  CMDVDVNO  = MVCField(MVCTypeField+MVCTypeList, String(3), label='Division', charcase = ecUpperCase)
  CMDVDVNM  = MVCField(MVCTypeField+MVCTypeList, String(24), label='Name', synchronized=True)
  CMDVDVDS  = MVCField(MVCTypeField+MVCTypeList, String(48), label='Description')
  CMDVADR1  = MVCField(MVCTypeField, String(48), label='Address')
  CMDVADR2  = MVCField(MVCTypeField, String(48), label='Address')
  CMDVADR3  = MVCField(MVCTypeField, String(48), label='Address')
  CMDVZIPC  = MVCField(MVCTypeField, String(48), label='Zip')
  CMDVARID  = MVCField(MVCTypeField, String(6), label='Area', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDVARNM  = MVCField(MVCTypeField, String(16), label='Area', enabled=False)
  CMDVSTID  = MVCField(MVCTypeField, String(6), label='State', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDVSTNM  = MVCField(MVCTypeField, String(16), label='State', enabled=False)
  CMDVCTID  = MVCField(MVCTypeField, String(2), label='Country', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDVCTNM  = MVCField(MVCTypeField, String(16), label='Country', enabled=False)
  CMDVPHN1  = MVCField(MVCTypeField, String(24), label='Phone')
  CMDVPHN2  = MVCField(MVCTypeField, String(24), label='Phone')
  CMDVFAX1  = MVCField(MVCTypeField, String(24), label='Fax')
  CMDVFAX2  = MVCField(MVCTypeField, String(24), label='Fax')
  CMDVXEML  = MVCField(MVCTypeField, String(32), label='email')
  CMDVWURL  = MVCField(MVCTypeField, String(48), label='URL')

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = ( MVCExtFunction('Company Identification', 'CMN100'),
      MVCExtFunction('Facilities', 'CMN120')
      )
    return mvcsession


  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    if params['CMDVCONO'] is not None:
      query = query.filter_by(CMDVCONO = params['CMDVCONO'])
    return query


  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if (fieldName == 'CMDVCONO'):
      ret.svcname = 'CMN100'
      ret.retfield = 'CMCPCONO'
    if (fieldName == 'CMDVARID'):
      ret.svcname = 'CMN030'
      ret.retfield = 'CMARIDCD'
    if fieldName == 'CMDVSTID':
      ret.svcname = 'CMN020'
      ret.retfield = 'CMSTIDCD'
    if fieldName == 'CMDVCTID':
      ret.svcname = 'CMN010'
      ret.retfield = 'CMCTIDCD'
    return ret

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (fieldName == 'CMDVDVNM') and \
       (fields['CMDVDVNM'] != '') and \
       (fields['CMDVDVDS'] in (None, '')):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDVDVDS', fields['CMDVDVNM'])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDVARID'):
      usrobj = proxy.getObject('USROBJ')
      cmnobj = proxy.getObject('CMNOBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      arinfo = cmnobj.getArea( usrinfo['USRCONO'], fields['CMDVARID'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDVARID', arinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMDVARNM', arinfo[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDVSTID'):
      usrobj = proxy.getObject('USROBJ')
      cmnobj = proxy.getObject('CMNOBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      stinfo = cmnobj.getState( usrinfo['USRCONO'], fields['CMDVSTID'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDVSTID', stinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMDVSTNM', stinfo[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDVCTID'):
      cmnobj = proxy.getObject('CMNOBJ')
      ctrinfo = cmnobj.getCountry( fields['CMDVCTID'] )
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDVCTID', ctrinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMDVCTNM', ctrinfo[1])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDVCONO'):
      proxy = self.getBusinessObjectProxy()
      cmpobj = proxy.getObject('CMPOBJ')
      if cmpobj:
        restuple = cmpobj.getCompany( fields['CMDVCONO'] )
        mvcsession.entryDataset.Edit()
        mvcsession.entryDataset.SetFieldValue('CMDVCONO', restuple[0])
        mvcsession.entryDataset.SetFieldValue('CMDVCONM', restuple[1])
        mvcsession.entryDataset.Post()
    return mvcsession

  def initializeData(self, mvcsession):
    '''Initializing data'''
    proxy = self.getBusinessObjectProxy()
    usrobj = proxy.getObject('USROBJ')
    info = usrobj.retrieveUserInfo(mvcsession)
    cono = info[2]
    if cono is None:
      cono = ''
    cmpobj = proxy.getObject('CMPOBJ')
    restuple = cmpobj.getCompany( cono )
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValue('CMDVCONO', restuple[0])
    mvcsession.entryDataset.SetFieldValue('CMDVCONM', restuple[1])
    mvcsession.entryDataset.Post()
    return mvcsession

  def afterPostData(self, mvcsession, obj):
    '''Event triggered after posting data'''
    proxy = self.getBusinessObjectProxy()
    cmpobj = proxy.getObject('CMPOBJ')
    if mvcsession.execType == MVCExecEdit:
      cmpobj.updateDIVICache(obj)
    elif mvcsession.execType == MVCExecDelete:
      cmpobj.removeDIVICache(obj)
    return (mvcsession, obj)











