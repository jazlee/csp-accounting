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
from tbl import CMPDPT

class CMN130(MVCController):
  """
  Departments
  """

  _description = 'Departments'
  _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
  _model_binder = MVCModelBinder(CMPDPT)

  CMDPDPNO  = MVCField(MVCTypeField + MVCTypeList, String(6), label='Dept', charcase=ecUpperCase)
  CMDPDPNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Name', synchronized=True)
  CMDPCONO  = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(3), label='Comp', charcase=ecUpperCase, enabled=False)
  CMDPDVNO  = MVCField(MVCTypeField + MVCTypeList + MVCTypeParam, String(3), label='Div', charcase=ecUpperCase, enabled=False)
  CMDPDPDS  = MVCField(MVCTypeField, String(48), label='Description')
  CMDPFANO  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Facility', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDPFANM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Facility', enabled=False)
  CMDPLCNO  = MVCField(MVCTypeField + MVCTypeList, String(3), label='Location', synchronized=True, browseable=True, charcase = ecUpperCase)
  CMDPLCNM  = MVCField(MVCTypeField + MVCTypeList, String(24), label='Location', enabled=False)

  def initView(self, mvcsession):
    '''Initialize the program'''
    mvcsession.extFunctions = ( MVCExtFunction('Facilities', 'CMN120'),
        MVCExtFunction('Location', 'CMN125'),
        MVCExtFunction('Sub-Department', 'CMN140'),
      )
    return mvcsession


  def lookupView(self, mvcsession, fieldName):
    '''Define lookup metadata for specified field'''
    ret = MVCLookupDef('','')
    if fieldName == 'CMDPFANO':
      ret.svcname = 'CMN120'
      ret.retfield = 'CMFAFANO'
    if fieldName == 'CMDPLCNO':
      ret.svcname = 'CMN125'
      ret.retfield = 'CMLOLCNO'
    return ret

  def initializeParam(self, mvcsession, query):
    '''Initialize parameters'''
    params = mvcsession.paramDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    if (params['CMDPCONO'] is None) or \
       (params['CMDPDVNO'] is None):
      usrobj= proxy.getObject('USROBJ')
      usrinfo = usrobj.retrieveUserInfoDict(mvcsession)
      params['CMDPCONO'], params['CMDPDVNO'] = usrinfo['USRCONO'], usrinfo['USRDVNO']

      mvcsession.paramDataset.Edit()
      mvcsession.paramDataset.SetFieldValues(params)
      mvcsession.paramDataset.Post()

    cmpobj = proxy.getObject('CMPOBJ')
    cmpobj.validateCompany(params['CMDPCONO'])
    cmpobj.validateDivision(params['CMDPCONO'], params['CMDPDVNO'])

    query = query.filter_by(CMDPCONO = params['CMDPCONO'])
    query = query.filter_by(CMDPDVNO = params['CMDPDVNO'])
    return query

  def initializeData(self, mvcsession):
    '''Initializing data'''
    params = mvcsession.paramDataset.FieldsAsDict()
    mvcsession.entryDataset.Append()
    mvcsession.entryDataset.SetFieldValues(params)
    mvcsession.entryDataset.Post()
    return mvcsession

  def synchronizeData(self, mvcsession, fieldName, fieldType):
    '''Synchronize data retrieved from user input'''
    fields = mvcsession.entryDataset.FieldsAsDict()
    proxy = self.getBusinessObjectProxy()
    cmpobj = proxy.getObject('CMPOBJ')
    if (fieldName == 'CMDPDPNM') and (fields['CMDPDPNM'] is not None) and \
       (fields['CMDPDPDS'] is None):
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDPDPDS', fields['CMDPDPNM'])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDPFANO'):
      facinfo = cmpobj.getFacility(fields['CMDPFANO'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDPCONO', facinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMDPDVNO', facinfo[2])
      mvcsession.entryDataset.SetFieldValue('CMDPFANO', facinfo[4])
      mvcsession.entryDataset.SetFieldValue('CMDPFANM', facinfo[5])
      mvcsession.entryDataset.Post()
    elif (fieldName == 'CMDPLCNO'):
      locinfo = cmpobj.getLocation(fields['CMDPLCNO'])
      mvcsession.entryDataset.Edit()
      mvcsession.entryDataset.SetFieldValue('CMDPCONO', locinfo[0])
      mvcsession.entryDataset.SetFieldValue('CMDPDVNO', locinfo[2])
      mvcsession.entryDataset.SetFieldValue('CMDPLCNO', locinfo[4])
      mvcsession.entryDataset.SetFieldValue('CMDPLCNM', locinfo[5])
      mvcsession.entryDataset.Post()
    return mvcsession



